#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { createHash, randomUUID } from "node:crypto";
import {
  appendFileSync,
  copyFileSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  realpathSync,
  statSync,
  writeFileSync,
} from "node:fs";
import {
  basename,
  dirname,
  isAbsolute,
  join,
  relative,
  resolve,
  sep,
} from "node:path";
import { fileURLToPath } from "node:url";

const VERSION_PATTERNS = Object.freeze({
  dev: /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.dev(0|[1-9][0-9]*)$/,
  production:
    /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:rc(0|[1-9][0-9]*))?$/,
});

const OUTPUT_NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/;
const SHA_PATTERN = /^[0-9a-f]{40}$/;
const CHANGELOG_CATEGORIES = Object.freeze([
  "Added",
  "Changed",
  "Fixed",
  "Deprecated",
  "Removed",
]);
const READTHEDOCS_API_BASE = "https://readthedocs.org/api/v3";
const CLI_USAGE = `Usage: node .github/scripts/release-tools.mjs <command> [options]

Shared release commands:
  derive                  Validate a version and write derived release outputs
  prepare-dev-source      Copy tracked files and rewrite py-cord as py-cord-dev
  stage-artifacts         Validate and stage the exact wheel and source archive
  validate-artifacts      Validate exact channel-specific distribution files
  check-tag               Classify the remote annotated tag state
  check-github-release    Validate release metadata, immutability, and asset digests
  check-immutable         Require the repository immutable-release setting
  check-pypi-unused       Require an unpublished PyPI version
  check-pypi-published    Match published PyPI files to local artifacts
  source-date-epoch       Derive a reproducible-build timestamp from a commit
  release-history         Derive previous production tags without shell parsing
  check-changelog         Require a prepared production changelog entry
  check-github-identity   Require an exact GitHub automation identity
  resolve-tag             Resolve and validate an existing annotated tag

Production migration commands:
  update-changelog        Generate the production changelog section and links
  rtd-release             Sync, wait for, and activate a Read the Docs version
  notify-discord          Render or send the production Discord announcement
  milestone-candidates    Derive exact compatible milestone titles
  close-milestone         Close the exact milestone for a published release
`;

function fail(message) {
  throw new Error(message);
}

function requireString(value, label) {
  if (typeof value !== "string" || value.length === 0) {
    fail(`${label} must be a non-empty string`);
  }
  if (value.includes("\0")) {
    fail(`${label} must not contain a NUL byte`);
  }
  return value;
}

function requireSha(value, label = "commit") {
  const sha = requireString(value, label).toLowerCase();
  if (!SHA_PATTERN.test(sha)) {
    fail(`${label} must be a full 40-character lowercase Git SHA`);
  }
  return sha;
}

function requireTag(value) {
  const tag = requireString(value, "tag");
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(tag)) {
    fail(`invalid Git tag '${tag}'`);
  }
  return tag;
}

export function parseReleaseVersion(channel, version) {
  if (!Object.hasOwn(VERSION_PATTERNS, channel)) {
    fail(`unsupported release channel '${channel}'`);
  }

  const candidate = requireString(version, "version");
  const match = VERSION_PATTERNS[channel].exec(candidate);
  if (!match) {
    const expected = channel === "dev" ? "X.Y.Z.devN" : "X.Y.Z or X.Y.ZrcN";
    fail(
      `invalid ${channel} version '${candidate}'; expected canonical ${expected}`,
    );
  }

  return Object.freeze({
    channel,
    version: candidate,
    major: Number(match[1]),
    minor: Number(match[2]),
    patch: Number(match[3]),
    prereleaseNumber: match[4] === undefined ? null : Number(match[4]),
    isPrerelease: channel === "dev" || match[4] !== undefined,
  });
}

export function deriveRelease(channel, version) {
  const parsed = parseReleaseVersion(channel, version);
  if (channel === "dev") {
    return Object.freeze({
      ...parsed,
      distribution: "py-cord-dev",
      normalizedDistribution: "py_cord_dev",
      tag: `dev-v${version}`,
      title: `Pycord Development ${version}`,
      versionBranch: null,
      wheelName: `py_cord_dev-${version}-py3-none-any.whl`,
      sdistName: `py_cord_dev-${version}.tar.gz`,
    });
  }

  return Object.freeze({
    ...parsed,
    distribution: "py-cord",
    normalizedDistribution: "py_cord",
    tag: `v${version}`,
    title: `v${version}`,
    versionBranch: `v${parsed.major}.${parsed.minor}.x`,
    wheelName: `py_cord-${version}-py3-none-any.whl`,
    sdistName: `py_cord-${version}.tar.gz`,
  });
}

export function milestoneTitleCandidates(version) {
  const release = deriveRelease("production", version);
  const candidates = [release.version, release.tag];
  if (release.prereleaseNumber !== null) {
    const dotted = release.version.replace(/rc([0-9]+)$/, "rc.$1");
    candidates.push(dotted, `v${dotted}`);
  }
  return Object.freeze([...new Set(candidates)]);
}

export function classifyMilestoneState(version, milestones) {
  if (!Array.isArray(milestones)) {
    fail("milestones must be an array");
  }
  const candidates = milestoneTitleCandidates(version);
  const matches = milestones.filter(
    (milestone) =>
      milestone &&
      typeof milestone.title === "string" &&
      candidates.includes(milestone.title),
  );
  if (matches.length > 1) {
    fail(
      `multiple milestones match ${version}: ${matches.map((item) => item.title).join(", ")}`,
    );
  }
  return Object.freeze({
    state: matches.length === 0 ? "absent" : "matched",
    candidates,
    milestone: matches[0] ?? null,
  });
}

export async function fetchGitHubMilestones(
  repository,
  token,
  fetchImplementation = globalThis.fetch,
) {
  const repo = requireRepository(repository);
  const authToken = requireString(token, "GitHub token");
  const milestones = [];
  for (let page = 1; page <= 100; page += 1) {
    const response = await fetchImplementation(
      `https://api.github.com/repos/${repo}/milestones?state=all&per_page=100&page=${page}`,
      {
        headers: {
          Accept: "application/vnd.github+json",
          Authorization: `Bearer ${authToken}`,
          "X-GitHub-Api-Version": "2022-11-28",
        },
        redirect: "error",
        cache: "no-store",
      },
    );
    if (!response.ok) {
      await responseError(response, `GitHub milestone lookup for ${repo}`);
    }
    const pageItems = await response.json();
    if (!Array.isArray(pageItems)) {
      fail("GitHub milestone response must be an array");
    }
    milestones.push(...pageItems);
    if (pageItems.length < 100) {
      return milestones;
    }
  }
  fail("GitHub milestone lookup exceeded 100 pages");
}

export async function closeReleaseMilestone(
  { repository, version, token = null, dryRun = false },
  fetchImplementation = globalThis.fetch,
) {
  const repo = requireRepository(repository);
  deriveRelease("production", version);
  const authToken = requireString(token, "GitHub token");
  const milestones = await fetchGitHubMilestones(
    repo,
    authToken,
    fetchImplementation,
  );
  const match = classifyMilestoneState(version, milestones);
  if (match.state === "absent") {
    fail(
      `no milestone matches release ${version}; expected one of: ${match.candidates.join(", ")}`,
    );
  }

  const milestone = match.milestone;
  if (!Number.isInteger(milestone.number) || milestone.number < 1) {
    fail(`milestone '${milestone.title}' has an invalid number`);
  }
  if (milestone.state !== "open" && milestone.state !== "closed") {
    fail(
      `milestone '${milestone.title}' has invalid state '${milestone.state}'`,
    );
  }
  const result = {
    number: milestone.number,
    title: milestone.title,
    openIssues: Number.isInteger(milestone.open_issues)
      ? milestone.open_issues
      : null,
    alreadyClosed: milestone.state === "closed",
    dryRun: Boolean(dryRun),
    closed: milestone.state === "closed",
  };
  if (milestone.state === "closed" || dryRun) {
    return Object.freeze(result);
  }

  const response = await fetchImplementation(
    `https://api.github.com/repos/${repo}/milestones/${milestone.number}`,
    {
      method: "PATCH",
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${authToken}`,
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      body: JSON.stringify({ state: "closed" }),
      redirect: "error",
    },
  );
  if (!response.ok) {
    await responseError(
      response,
      `closing GitHub milestone '${milestone.title}'`,
    );
  }
  const updated = await response.json();
  if (updated.number !== milestone.number || updated.state !== "closed") {
    fail(`GitHub did not report milestone '${milestone.title}' as closed`);
  }
  return Object.freeze({ ...result, closed: true });
}

function requireRepository(value) {
  const repository = requireString(value, "repository");
  if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repository)) {
    fail(`invalid GitHub repository '${repository}'`);
  }
  return repository;
}

export function buildUnreleasedChangelogBlock(branch) {
  const branchName = requireString(branch, "branch");
  return [
    "## [Unreleased]",
    "",
    `These changes are available on the \`${branchName}\` branch, but have not yet been released.`,
    "",
    "### Added",
    "",
    "### Changed",
    "",
    "### Fixed",
    "",
    "### Deprecated",
    "",
    "### Removed",
    "",
  ].join("\n");
}

export function parseChangelogCategories(sectionBody) {
  const categories = Object.fromEntries(
    CHANGELOG_CATEGORIES.map((name) => [name, []]),
  );
  let current = null;
  for (const line of requireString(
    sectionBody || "\n",
    "changelog section",
  ).split(/\r?\n/)) {
    const heading = /^###\s+(.+)$/.exec(line);
    if (heading) {
      current = Object.hasOwn(categories, heading[1].trim())
        ? heading[1].trim()
        : null;
      continue;
    }
    if (current !== null) {
      categories[current].push(line);
    }
  }
  return categories;
}

function mergeChangelogCategories(destination, source) {
  for (const category of CHANGELOG_CATEGORIES) {
    destination[category].push(...source[category]);
  }
}

export function renderChangelogReleaseBody(categories) {
  const parts = [];
  for (const category of CHANGELOG_CATEGORIES) {
    const lines = (categories[category] ?? []).filter(
      (line) => line.trim() !== "",
    );
    if (lines.length === 0) {
      continue;
    }
    parts.push(`### ${category}`, "", ...lines, "");
  }
  return parts.join("\n").replace(/\n+$/, "");
}

function replaceOrAppendChangelogLinks(
  text,
  version,
  previousTag,
  previousFinalTag,
  repository,
) {
  const unreleasedLink = `[unreleased]: https://github.com/${repository}/compare/v${version}...HEAD`;
  const baseTag = version.includes("rc")
    ? previousTag
    : previousFinalTag || previousTag;
  const releaseLink = `[${version}]: https://github.com/${repository}/compare/${baseTag}...v${version}`;

  let updated = text.replace(/^\[unreleased]: .*$/m, unreleasedLink);
  const escapedVersion = version.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const versionLink = new RegExp(`^\\[${escapedVersion}]: .*$`, "m");
  if (versionLink.test(updated)) {
    return updated.replace(versionLink, releaseLink);
  }
  if (/^\[unreleased]: .*$/m.test(updated)) {
    return updated.replace(
      /^\[unreleased]: .*$/m,
      (match) => `${match}\n${releaseLink}`,
    );
  }
  return `${updated.replace(/\n+$/, "")}\n${releaseLink}\n`;
}

export function updateChangelogText({
  text,
  version,
  previousTag,
  previousFinalTag = null,
  branch,
  repository,
  date,
}) {
  const contents = requireString(text, "changelog");
  deriveRelease("production", version);
  const escapedHeadingVersion = version.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  if (
    new RegExp(`^## \\[${escapedHeadingVersion}](?:\\s|$)`, "m").test(contents)
  ) {
    fail(`changelog already contains a release section for ${version}`);
  }
  requireString(previousTag, "previous tag");
  if (previousFinalTag !== null) {
    requireString(previousFinalTag, "previous final tag");
  }
  requireRepository(repository);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(requireString(date, "release date"))) {
    fail(`invalid release date '${date}'; expected YYYY-MM-DD`);
  }

  const unreleasedHeading = /^## \[Unreleased]\s*$/m.exec(contents);
  if (!unreleasedHeading) {
    fail("missing '## [Unreleased]' heading in changelog");
  }
  const start = unreleasedHeading.index;
  const bodyStart = contents.indexOf("\n", start) + 1;
  const followingHeader = /^## \[/m.exec(contents.slice(bodyStart));
  const end = followingHeader
    ? bodyStart + followingHeader.index
    : contents.length;
  const unreleasedBody = contents.slice(bodyStart, end).replace(/\n+$/, "");
  const rest = contents.slice(end);

  const aggregated = parseChangelogCategories(unreleasedBody);
  if (!version.includes("rc")) {
    const sectionPattern = /^## \[([^\]]+)]([^\n]*)\n/gm;
    const matches = [...rest.matchAll(sectionPattern)];
    const basePrefix = `${version}rc`;
    let collecting = false;
    for (let index = 0; index < matches.length; index += 1) {
      const match = matches[index];
      const isReleaseCandidate = match[1].startsWith(basePrefix);
      if (isReleaseCandidate && !collecting) {
        collecting = true;
      }
      if (collecting && !isReleaseCandidate) {
        break;
      }
      if (!collecting) {
        continue;
      }
      const rcBodyStart = match.index + match[0].length;
      const rcBodyEnd =
        index + 1 < matches.length ? matches[index + 1].index : rest.length;
      mergeChangelogCategories(
        aggregated,
        parseChangelogCategories(
          rest.slice(rcBodyStart, rcBodyEnd).replace(/\n+$/, ""),
        ),
      );
    }
  }

  const releaseBody = renderChangelogReleaseBody(aggregated);
  const releaseSection = `## [${version}] - ${date}\n${releaseBody}\n`;
  let updated = `${contents.slice(0, start)}${buildUnreleasedChangelogBlock(branch)}\n${releaseSection}${rest}`;
  updated = replaceOrAppendChangelogLinks(
    updated,
    version,
    previousTag,
    previousFinalTag,
    repository,
  );
  return updated.endsWith("\n") ? updated : `${updated}\n`;
}

export function assertChangelogPreparedText(text, version, repository) {
  const contents = requireString(text, "changelog");
  deriveRelease("production", version);
  const repo = requireRepository(repository);
  const escapedVersion = version.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const headings =
    contents.match(
      new RegExp(`^## \\[${escapedVersion}] - \\d{4}-\\d{2}-\\d{2}$`, "gm"),
    ) ?? [];
  if (headings.length !== 1) {
    fail(
      `expected exactly one dated changelog section for ${version}, found ${headings.length}`,
    );
  }
  const releaseLink = new RegExp(
    `^\\[${escapedVersion}]: https://github\\.com/${repo.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}/compare/.+\\.\\.\\.v${escapedVersion}$`,
    "m",
  );
  if (!releaseLink.test(contents)) {
    fail(`changelog is missing the compare link for ${version}`);
  }
  const unreleasedLink = `[unreleased]: https://github.com/${repo}/compare/v${version}...HEAD`;
  if (!contents.split(/\r?\n/).includes(unreleasedLink)) {
    fail(`changelog Unreleased link does not start at v${version}`);
  }
  return Object.freeze({ version, prepared: true });
}

export function updateChangelogFile(options) {
  const changelogPath = resolve(requireString(options.path, "changelog path"));
  if (!existsSync(changelogPath) || !lstatSync(changelogPath).isFile()) {
    fail(`changelog not found at '${changelogPath}'`);
  }
  const updated = updateChangelogText({
    ...options,
    text: readFileSync(changelogPath, "utf8"),
  });
  writeFileSync(changelogPath, updated, "utf8");
  return Object.freeze({ path: changelogPath, version: options.version });
}

export function deriveReadTheDocsRelease(version) {
  const release = deriveRelease("production", version);
  return Object.freeze({
    version: release.version,
    docsVersion: release.isPrerelease ? release.versionBranch : release.tag,
    hidden: release.isPrerelease,
  });
}

async function responseError(response, operation) {
  let detail = "";
  try {
    detail = (await response.text()).slice(0, 500).replace(/[\r\n]+/g, " ");
  } catch {
    // The status is still sufficient when the response body cannot be read.
  }
  fail(
    `${operation} failed with HTTP ${response.status}${detail ? `: ${detail}` : ""}`,
  );
}

function delay(milliseconds) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, milliseconds));
}

export async function manageReadTheDocsRelease(
  {
    project = "pycord",
    version,
    token = null,
    sync = false,
    dryRun = false,
    attempts = 12,
    retryDelayMs = 5_000,
  },
  dependencies = {},
) {
  const projectSlug = requireString(project, "Read the Docs project");
  if (!/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(projectSlug)) {
    fail(`invalid Read the Docs project '${projectSlug}'`);
  }
  const plan = deriveReadTheDocsRelease(version);
  const result = Object.freeze({
    project: projectSlug,
    ...plan,
    sync: Boolean(sync),
  });
  if (dryRun) {
    return result;
  }
  const authToken = requireString(token, "Read the Docs token");
  if (!Number.isInteger(attempts) || attempts < 1 || attempts > 60) {
    fail("Read the Docs attempts must be an integer from 1 to 60");
  }
  if (
    !Number.isInteger(retryDelayMs) ||
    retryDelayMs < 0 ||
    retryDelayMs > 60_000
  ) {
    fail(
      "Read the Docs retry delay must be an integer from 0 to 60000 milliseconds",
    );
  }
  const fetchImplementation =
    dependencies.fetchImplementation ?? globalThis.fetch;
  const delayImplementation = dependencies.delayImplementation ?? delay;
  const headers = {
    Authorization: `Token ${authToken}`,
    "Content-Type": "application/json",
  };
  const projectUrl = `${READTHEDOCS_API_BASE}/projects/${encodeURIComponent(projectSlug)}`;

  if (sync) {
    const syncResponse = await fetchImplementation(
      `${projectUrl}/sync-versions/`,
      {
        method: "POST",
        headers,
        body: "{}",
      },
    );
    if (!syncResponse.ok) {
      await responseError(
        syncResponse,
        `Read the Docs sync for ${projectSlug}`,
      );
    }
  }

  const versionUrl = `${projectUrl}/versions/${encodeURIComponent(plan.docsVersion)}/`;
  if (sync) {
    let available = false;
    for (let attempt = 1; attempt <= attempts; attempt += 1) {
      const response = await fetchImplementation(versionUrl, {
        method: "GET",
        headers,
      });
      if (response.ok) {
        available = true;
        break;
      }
      if (response.status !== 404) {
        await responseError(
          response,
          `Read the Docs version lookup for ${plan.docsVersion}`,
        );
      }
      if (attempt < attempts) {
        await delayImplementation(retryDelayMs);
      }
    }
    if (!available) {
      fail(
        `Read the Docs version '${plan.docsVersion}' did not appear after ${attempts} attempts`,
      );
    }
  }

  const activationResponse = await fetchImplementation(versionUrl, {
    method: "PATCH",
    headers,
    body: JSON.stringify({ active: true, hidden: plan.hidden }),
  });
  if (!activationResponse.ok) {
    await responseError(
      activationResponse,
      `Read the Docs activation for ${plan.docsVersion}`,
    );
  }
  return result;
}

export function buildDiscordReleaseMessage({
  version,
  previousTag,
  previousFinalTag = null,
  repository,
}) {
  const release = deriveRelease("production", version);
  const previous = requireString(previousTag, "previous tag");
  const previousFinal = previousFinalTag
    ? requireString(previousFinalTag, "previous final tag")
    : previous;
  const repo = requireRepository(repository);
  const majorMinor = `${release.major}.${release.minor}`;
  const docsUrl = `https://docs.pycord.dev/en/v${version}/changelog.html`;
  const baseCompare = release.isPrerelease ? previous : previousFinal;
  const compareUrl = `https://github.com/${repo}/compare/${baseCompare}...v${version}`;
  const releaseUrl = `https://github.com/${repo}/releases/tag/v${version}`;
  const pypiUrl = `https://pypi.org/project/py-cord/${version}/`;

  if (release.isPrerelease) {
    return (
      `## <:pycord:1063211537008955495> Pycord v${version} Release Candidate (${majorMinor}) is available!\n\n` +
      "@here\n\n" +
      "This is a pre-release (release candidate) for testing and feedback.\n\n" +
      `You can view the changelog here: <${docsUrl}>\n\n` +
      `Check out the [GitHub changelog](<${compareUrl}>), [GitHub release page](<${releaseUrl}>), and [PyPI release page](<${pypiUrl}>).\n\n` +
      `You can install this version by running the following command:\n\`\`\`sh\npip install -U py-cord==${version}\n\`\`\`\n\n` +
      "Please try it out and let us know your feedback or any issues!"
    );
  }

  return (
    `## <:pycord:1063211537008955495> Pycord v${version} is out!\n\n` +
    "@everyone\n\n" +
    `You can view the changelog here: <${docsUrl}>\n\n` +
    `Feel free to take a look at the [GitHub changelog](<${compareUrl}>), [GitHub release page](<${releaseUrl}>) and the [PyPI release page](<${pypiUrl}>).\n\n` +
    `You can install this version by running the following command:\n\`\`\`sh\npip install -U py-cord==${version}\n\`\`\``
  );
}

export function buildDiscordReleasePayload(options) {
  return Object.freeze({
    content: buildDiscordReleaseMessage(options),
    allowed_mentions: { parse: ["everyone", "roles"] },
  });
}

export async function sendDiscordReleaseNotification(
  options,
  fetchImplementation = globalThis.fetch,
) {
  const payload = buildDiscordReleasePayload(options);
  if (options.dryRun) {
    return Object.freeze({ payload, sent: false });
  }
  const webhook = new URL(
    requireString(options.webhookUrl, "Discord webhook URL"),
  );
  if (
    webhook.protocol !== "https:" ||
    !["discord.com", "discordapp.com"].includes(webhook.hostname) ||
    !webhook.pathname.startsWith("/api/webhooks/")
  ) {
    fail("Discord webhook URL must be an HTTPS discord.com API webhook URL");
  }
  const response = await fetchImplementation(webhook, {
    method: "POST",
    headers: {
      Accept: "*/*",
      "Content-Type": "application/json",
      "User-Agent":
        "pycord-release-bot/1.0 (+https://github.com/Pycord-Development/pycord)",
    },
    body: JSON.stringify(payload),
    redirect: "error",
  });
  if (!response.ok) {
    await responseError(response, "Discord release notification");
  }
  return Object.freeze({ payload, sent: true });
}

function outputValue(value) {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

export function formatGitHubOutputs(
  outputs,
  delimiterFactory = () => `ghadelimiter_${randomUUID()}`,
) {
  if (!outputs || typeof outputs !== "object" || Array.isArray(outputs)) {
    fail("GitHub outputs must be an object");
  }

  let result = "";
  for (const [name, rawValue] of Object.entries(outputs)) {
    if (!OUTPUT_NAME_PATTERN.test(name)) {
      fail(`invalid GitHub output name '${name}'`);
    }
    const value = outputValue(rawValue);
    if (value.includes("\0")) {
      fail(`GitHub output '${name}' must not contain a NUL byte`);
    }

    let delimiter;
    do {
      delimiter = requireString(delimiterFactory(), "GitHub output delimiter");
    } while (value.split(/\r?\n/).includes(delimiter));
    result += `${name}<<${delimiter}\n${value}\n${delimiter}\n`;
  }
  return result;
}

export function writeGitHubOutputs(outputPath, outputs) {
  const destination = requireString(outputPath, "GitHub output path");
  appendFileSync(destination, formatGitHubOutputs(outputs), {
    encoding: "utf8",
  });
}

function isInsideOrEqual(root, candidate) {
  const rel = relative(root, candidate);
  return (
    rel === "" ||
    (!rel.startsWith(`..${sep}`) && rel !== ".." && !isAbsolute(rel))
  );
}

function validateTrackedPath(file) {
  const candidate = requireString(file, "tracked path");
  if (
    candidate.startsWith("/") ||
    candidate.startsWith("\\") ||
    /^[A-Za-z]:[\\/]/.test(candidate)
  ) {
    fail(`tracked path '${candidate}' must be relative`);
  }
  const parts = candidate.split(/[\\/]/);
  if (parts.some((part) => part === "" || part === "." || part === "..")) {
    fail(`tracked path '${candidate}' contains an unsafe component`);
  }
  return parts;
}

export function rewriteProjectNameText(contents) {
  const text = requireString(contents, "pyproject contents");
  const lines = text.split(/(?<=\n)/);
  let inProject = false;
  let projectTables = 0;
  let assignments = 0;

  const rewritten = lines.map((line) => {
    const bareLine = line.replace(/[\r\n]+$/, "");
    const table = /^\s*\[([^\]]+)]\s*(?:#.*)?$/.exec(bareLine);
    if (table) {
      inProject = table[1] === "project";
      if (inProject) {
        projectTables += 1;
      }
      return line;
    }

    if (!inProject || !/^\s*name\s*=/.test(bareLine)) {
      return line;
    }

    assignments += 1;
    const assignment =
      /^(\s*name\s*=\s*)(["'])([^"']*)(\2)(\s*(?:#.*)?)(\r?\n)?$/.exec(line);
    if (!assignment) {
      fail("[project].name must be a simple quoted string");
    }
    if (assignment[3] !== "py-cord") {
      fail(
        `[project].name must be exactly 'py-cord', found '${assignment[3]}'`,
      );
    }
    return `${assignment[1]}${assignment[2]}py-cord-dev${assignment[4]}${assignment[5]}${assignment[6] ?? ""}`;
  });

  if (projectTables !== 1) {
    fail(`expected exactly one [project] table, found ${projectTables}`);
  }
  if (assignments !== 1) {
    fail(
      `expected exactly one [project].name assignment, found ${assignments}`,
    );
  }
  return rewritten.join("");
}

export function listTrackedFiles(sourceDirectory) {
  const source = realpathSync(
    requireString(sourceDirectory, "source directory"),
  );
  const output = execFileSync(
    "git",
    ["-C", source, "ls-files", "-z", "--cached"],
    {
      encoding: "utf8",
      maxBuffer: 32 * 1024 * 1024,
      windowsHide: true,
    },
  );
  return output.split("\0").filter(Boolean);
}

export function parseSourceDateEpoch(value) {
  const epoch = requireString(value, "source date epoch").trim();
  if (!/^(0|[1-9][0-9]*)$/.test(epoch)) {
    fail(`invalid source date epoch '${epoch}'`);
  }
  return epoch;
}

export function deriveSourceDateEpoch(repositoryDirectory, commit) {
  const repository = realpathSync(
    requireString(repositoryDirectory, "repository directory"),
  );
  const commitSha = requireSha(commit, "source commit");
  const output = execFileSync(
    "git",
    ["-C", repository, "show", "-s", "--format=%ct", commitSha],
    {
      encoding: "utf8",
      maxBuffer: 1024 * 1024,
      windowsHide: true,
    },
  );
  return parseSourceDateEpoch(output);
}

export function prepareDevSource(
  sourceDirectory,
  destinationDirectory,
  options = {},
) {
  const source = realpathSync(
    requireString(sourceDirectory, "source directory"),
  );
  const destinationInput = resolve(
    requireString(destinationDirectory, "destination directory"),
  );
  if (existsSync(destinationInput)) {
    fail(`destination '${destinationInput}' already exists`);
  }

  const destinationParent = realpathSync(dirname(destinationInput));
  const destination = join(destinationParent, basename(destinationInput));
  if (
    isInsideOrEqual(source, destination) ||
    isInsideOrEqual(destination, source)
  ) {
    fail("source and destination must not overlap");
  }

  const trackedFiles = options.trackedFiles ?? listTrackedFiles(source);
  if (!Array.isArray(trackedFiles) || trackedFiles.length === 0) {
    fail("tracked file list must be a non-empty array");
  }

  const validated = [];
  const seen = new Set();
  for (const trackedFile of trackedFiles) {
    const parts = validateTrackedPath(trackedFile);
    const normalized = parts.join("/");
    if (seen.has(normalized)) {
      fail(`duplicate tracked path '${normalized}'`);
    }
    seen.add(normalized);

    const sourcePath = resolve(source, ...parts);
    if (!isInsideOrEqual(source, sourcePath)) {
      fail(`tracked path '${trackedFile}' escapes the source directory`);
    }
    const info = lstatSync(sourcePath);
    if (info.isSymbolicLink()) {
      fail(`tracked path '${trackedFile}' is a symbolic link`);
    }
    if (!info.isFile()) {
      fail(`tracked path '${trackedFile}' is not a regular file`);
    }
    const realSourcePath = realpathSync(sourcePath);
    if (!isInsideOrEqual(source, realSourcePath)) {
      fail(
        `tracked path '${trackedFile}' resolves outside the source directory`,
      );
    }

    const destinationPath = resolve(destination, ...parts);
    if (!isInsideOrEqual(destination, destinationPath)) {
      fail(`tracked path '${trackedFile}' escapes the destination directory`);
    }
    validated.push({ normalized, sourcePath: realSourcePath, destinationPath });
  }

  const pyproject = validated.find(
    (file) => file.normalized === "pyproject.toml",
  );
  if (!pyproject) {
    fail("pyproject.toml must be Git-tracked");
  }
  const rewrittenPyproject = rewriteProjectNameText(
    readFileSync(pyproject.sourcePath, "utf8"),
  );

  mkdirSync(destination);
  for (const file of validated) {
    mkdirSync(dirname(file.destinationPath), { recursive: true });
    copyFileSync(file.sourcePath, file.destinationPath);
  }
  writeFileSync(pyproject.destinationPath, rewrittenPyproject, "utf8");

  return Object.freeze({ source, destination, fileCount: validated.length });
}

export function sha256File(filePath) {
  const file = resolve(requireString(filePath, "artifact path"));
  const info = lstatSync(file);
  if (!info.isFile() || info.isSymbolicLink()) {
    fail(`artifact '${file}' must be a regular file`);
  }
  return `sha256:${createHash("sha256").update(readFileSync(file)).digest("hex")}`;
}

export function validateArtifacts(channel, version, distDirectory) {
  const release = deriveRelease(channel, version);
  const distDir = realpathSync(
    requireString(distDirectory, "distribution directory"),
  );
  const entries = readdirSync(distDir, { withFileTypes: true });
  const names = entries.map((entry) => entry.name).sort();
  const expectedNames = [release.sdistName, release.wheelName].sort();

  if (entries.some((entry) => !entry.isFile() || entry.isSymbolicLink())) {
    fail("distribution directory must contain regular files only");
  }
  if (
    names.length !== expectedNames.length ||
    names.some((name, index) => name !== expectedNames[index])
  ) {
    fail(
      `expected exactly ${expectedNames.join(" and ")}; found ${names.join(", ") || "nothing"}`,
    );
  }

  const wheelPath = join(distDir, release.wheelName);
  const sdistPath = join(distDir, release.sdistName);
  return Object.freeze({
    distDir,
    wheelName: release.wheelName,
    wheelPath,
    wheelDigest: sha256File(wheelPath),
    wheelSize: statSync(wheelPath).size,
    sdistName: release.sdistName,
    sdistPath,
    sdistDigest: sha256File(sdistPath),
    sdistSize: statSync(sdistPath).size,
  });
}

export function stageArtifacts(
  channel,
  version,
  sourceDirectory,
  destinationDirectory,
) {
  const sourceArtifacts = validateArtifacts(channel, version, sourceDirectory);
  const destination = resolve(
    requireString(destinationDirectory, "artifact staging directory"),
  );
  if (existsSync(destination)) {
    fail(`artifact staging directory '${destination}' already exists`);
  }
  const destinationParent = realpathSync(dirname(destination));
  const canonicalDestination = join(destinationParent, basename(destination));
  if (isInsideOrEqual(sourceArtifacts.distDir, canonicalDestination)) {
    fail(
      "artifact staging directory must not be inside the build distribution directory",
    );
  }

  mkdirSync(canonicalDestination);
  copyFileSync(
    sourceArtifacts.wheelPath,
    join(canonicalDestination, sourceArtifacts.wheelName),
  );
  copyFileSync(
    sourceArtifacts.sdistPath,
    join(canonicalDestination, sourceArtifacts.sdistName),
  );
  const staged = validateArtifacts(channel, version, canonicalDestination);
  if (
    staged.wheelDigest !== sourceArtifacts.wheelDigest ||
    staged.sdistDigest !== sourceArtifacts.sdistDigest
  ) {
    fail("staged artifact digests do not match the build outputs");
  }
  return staged;
}

export function parseRemoteTagOutput(output, tag) {
  const expectedRef = `refs/tags/${requireTag(tag)}`;
  const records = requireString(output || "\n", "git ls-remote output")
    .trim()
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => {
      const match = /^([0-9a-f]{40})\s+(.+)$/.exec(line);
      if (!match) {
        fail(`malformed git ls-remote line '${line}'`);
      }
      return { sha: match[1], ref: match[2] };
    })
    .filter(
      (record) =>
        record.ref === expectedRef || record.ref === `${expectedRef}^{}`,
    );
  return records;
}

export function resolveAnnotatedTagState(tag, records) {
  const tagName = requireTag(tag);
  if (!Array.isArray(records)) {
    fail("tag records must be an array");
  }
  const expectedRef = `refs/tags/${tagName}`;
  const direct = records.filter((record) => record.ref === expectedRef);
  const peeled = records.filter((record) => record.ref === `${expectedRef}^{}`);
  if (direct.length === 0 && peeled.length === 0) {
    return Object.freeze({ state: "absent", commit: null });
  }
  if (direct.length !== 1 || peeled.length !== 1) {
    fail(`tag '${tagName}' must exist exactly once as an annotated tag`);
  }
  return Object.freeze({
    state: "annotated",
    commit: requireSha(peeled[0].sha, "tag commit"),
  });
}

export function resolveRemoteAnnotatedTag(repositoryDirectory, remote, tag) {
  const repository = realpathSync(
    requireString(repositoryDirectory, "repository directory"),
  );
  const remoteName = requireString(remote, "Git remote");
  if (!/^[A-Za-z0-9._-]+$/.test(remoteName)) {
    fail(`invalid Git remote '${remoteName}'`);
  }
  const tagName = requireTag(tag);
  const output = execFileSync(
    "git",
    [
      "-C",
      repository,
      "ls-remote",
      "--tags",
      remoteName,
      `refs/tags/${tagName}`,
      `refs/tags/${tagName}^{}`,
    ],
    { encoding: "utf8", maxBuffer: 1024 * 1024, windowsHide: true },
  );
  const state = resolveAnnotatedTagState(
    tagName,
    output.trim() ? parseRemoteTagOutput(output, tagName) : [],
  );
  if (state.state !== "annotated") {
    fail(`required annotated tag '${tagName}' does not exist`);
  }
  return state;
}

function compareParsedVersions(left, right) {
  for (const field of ["major", "minor", "patch"]) {
    if (left[field] !== right[field]) {
      return left[field] - right[field];
    }
  }
  if (left.prereleaseNumber === null && right.prereleaseNumber !== null) {
    return 1;
  }
  if (left.prereleaseNumber !== null && right.prereleaseNumber === null) {
    return -1;
  }
  return (left.prereleaseNumber ?? 0) - (right.prereleaseNumber ?? 0);
}

export function deriveReleaseHistory(version, tags) {
  const current = parseReleaseVersion("production", version);
  if (!Array.isArray(tags)) {
    fail("production tags must be an array");
  }
  const parsedTags = [];
  for (const rawTag of tags) {
    if (typeof rawTag !== "string" || !rawTag.startsWith("v")) {
      continue;
    }
    try {
      const parsed = parseReleaseVersion("production", rawTag.slice(1));
      if (compareParsedVersions(parsed, current) < 0) {
        parsedTags.push({ tag: rawTag, parsed });
      }
    } catch {
      // Historical noncanonical tags are intentionally ignored.
    }
  }
  parsedTags.sort((left, right) =>
    compareParsedVersions(right.parsed, left.parsed),
  );
  const previous = parsedTags[0];
  const previousFinal = parsedTags.find(
    (entry) => entry.parsed.prereleaseNumber === null,
  );
  if (!previous || !previousFinal) {
    fail(`could not determine previous production tags for ${version}`);
  }
  return Object.freeze({
    previousTag: previous.tag,
    previousFinalTag: previousFinal.tag,
  });
}

export function readReleaseHistory(repositoryDirectory, version) {
  const repository = realpathSync(
    requireString(repositoryDirectory, "repository directory"),
  );
  const output = execFileSync(
    "git",
    ["-C", repository, "tag", "--merged", "HEAD", "--list", "v*"],
    {
      encoding: "utf8",
      maxBuffer: 4 * 1024 * 1024,
      windowsHide: true,
    },
  );
  return deriveReleaseHistory(version, output.split(/\r?\n/).filter(Boolean));
}

export function classifyTagState(tag, expectedCommit, records) {
  const tagName = requireTag(tag);
  const expected = requireSha(expectedCommit, "expected tag commit");
  if (!Array.isArray(records)) {
    fail("tag records must be an array");
  }
  if (records.length === 0) {
    return Object.freeze({
      state: "absent",
      createTag: true,
      commit: null,
      reason: null,
    });
  }

  const expectedRef = `refs/tags/${tagName}`;
  const direct = records.filter((record) => record.ref === expectedRef);
  const peeled = records.filter((record) => record.ref === `${expectedRef}^{}`);
  if (direct.length !== 1 || peeled.length > 1) {
    return Object.freeze({
      state: "conflicting",
      createTag: false,
      commit: null,
      reason: "ambiguous tag refs",
    });
  }
  if (peeled.length === 0) {
    return Object.freeze({
      state: "conflicting",
      createTag: false,
      commit: direct[0].sha,
      reason: "existing tag is lightweight; an annotated tag is required",
    });
  }
  if (peeled[0].sha !== expected) {
    return Object.freeze({
      state: "conflicting",
      createTag: false,
      commit: peeled[0].sha,
      reason: `existing tag targets ${peeled[0].sha}, expected ${expected}`,
    });
  }
  return Object.freeze({
    state: "reusable",
    createTag: false,
    commit: expected,
    reason: null,
  });
}

export function readRemoteTagState(
  repositoryDirectory,
  remote,
  tag,
  expectedCommit,
) {
  const repository = realpathSync(
    requireString(repositoryDirectory, "repository directory"),
  );
  const remoteName = requireString(remote, "Git remote");
  if (!/^[A-Za-z0-9._-]+$/.test(remoteName)) {
    fail(`invalid Git remote '${remoteName}'`);
  }
  const tagName = requireTag(tag);
  const output = execFileSync(
    "git",
    [
      "-C",
      repository,
      "ls-remote",
      "--tags",
      remoteName,
      `refs/tags/${tagName}`,
      `refs/tags/${tagName}^{}`,
    ],
    { encoding: "utf8", maxBuffer: 1024 * 1024, windowsHide: true },
  );
  return classifyTagState(
    tagName,
    expectedCommit,
    output.trim() ? parseRemoteTagOutput(output, tagName) : [],
  );
}

function normalizeReleasePayload(payload) {
  if (payload === null) {
    return null;
  }
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    fail("release state must be a JSON object or null");
  }
  return {
    tagName: payload.tag_name ?? payload.tagName,
    title: payload.name,
    isDraft: payload.draft ?? payload.isDraft,
    isImmutable: payload.immutable ?? payload.isImmutable,
    isPrerelease: payload.prerelease ?? payload.isPrerelease,
    targetCommitish: payload.target_commitish ?? payload.targetCommitish,
    assets: payload.assets,
  };
}

export function classifyReleaseState(payload, expectedRelease, artifacts) {
  const release = normalizeReleasePayload(payload);
  if (release === null) {
    return Object.freeze({
      state: "absent",
      createRelease: true,
      resumeDraft: false,
      reuseRelease: false,
      wheelMissing: true,
      sdistMissing: true,
    });
  }
  if (
    expectedRelease.tagState !== undefined &&
    expectedRelease.tagState !== "reusable"
  ) {
    fail(
      `an existing release requires a reusable annotated tag, found '${expectedRelease.tagState}'`,
    );
  }

  const expectedCommit = requireSha(
    expectedRelease.commit,
    "expected release commit",
  );
  const required = {
    tagName: expectedRelease.tag,
    title: expectedRelease.title,
    isPrerelease: expectedRelease.isPrerelease ?? true,
    targetCommitish: expectedCommit,
  };
  for (const [field, value] of Object.entries(required)) {
    if (release[field] !== value) {
      fail(
        `release ${field} is ${JSON.stringify(release[field])}, expected ${JSON.stringify(value)}`,
      );
    }
  }
  if (!Array.isArray(release.assets)) {
    fail("release assets must be an array");
  }

  const expectedAssets = new Map([
    [
      artifacts.wheelName,
      { digest: artifacts.wheelDigest, size: artifacts.wheelSize },
    ],
    [
      artifacts.sdistName,
      { digest: artifacts.sdistDigest, size: artifacts.sdistSize },
    ],
  ]);
  const seen = new Set();
  for (const asset of release.assets) {
    if (!asset || typeof asset.name !== "string") {
      fail("release contains an asset without a valid name");
    }
    if (seen.has(asset.name)) {
      fail(`release contains duplicate asset '${asset.name}'`);
    }
    seen.add(asset.name);
    const expected = expectedAssets.get(asset.name);
    if (!expected) {
      fail(`release contains unexpected asset '${asset.name}'`);
    }
    if (asset.digest !== expected.digest) {
      fail(
        `release asset '${asset.name}' has digest ${asset.digest ?? "missing"}, expected ${expected.digest}`,
      );
    }
    if (asset.size !== expected.size) {
      fail(
        `release asset '${asset.name}' has size ${asset.size}, expected ${expected.size}`,
      );
    }
  }

  const wheelMissing = !seen.has(artifacts.wheelName);
  const sdistMissing = !seen.has(artifacts.sdistName);
  if (release.isDraft) {
    if (release.isImmutable !== false) {
      fail("a draft release must not be immutable");
    }
    return Object.freeze({
      state: "draft",
      createRelease: false,
      resumeDraft: true,
      reuseRelease: false,
      wheelMissing,
      sdistMissing,
    });
  }

  if (release.isImmutable !== true) {
    fail("a published release must be immutable");
  }
  if (wheelMissing || sdistMissing) {
    fail("a published release is missing an expected asset");
  }
  return Object.freeze({
    state: "published",
    createRelease: false,
    resumeDraft: false,
    reuseRelease: true,
    wheelMissing: false,
    sdistMissing: false,
  });
}

export async function fetchGitHubReleaseState(
  repository,
  tag,
  token,
  fetchImplementation = globalThis.fetch,
) {
  const repo = requireRepository(repository);
  const tagName = requireString(tag, "release tag");
  if (!/^[A-Za-z0-9._-]+$/.test(tagName)) {
    fail(`invalid release tag '${tagName}'`);
  }
  const authToken = requireString(token, "GitHub token");
  const response = await fetchImplementation(
    `https://api.github.com/repos/${repo}/releases/tags/${encodeURIComponent(tagName)}`,
    {
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${authToken}`,
        "X-GitHub-Api-Version": "2022-11-28",
      },
      redirect: "error",
      cache: "no-store",
    },
  );
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    await responseError(response, `GitHub release lookup for ${tagName}`);
  }
  return response.json();
}

export function assertImmutableReleaseSetting(payload) {
  if (!payload || typeof payload !== "object" || payload.enabled !== true) {
    fail("GitHub immutable releases must be enabled before running a release");
  }
  return Object.freeze({
    enabled: true,
    enforcedByOwner: payload.enforced_by_owner === true,
  });
}

export async function assertPypiVersionUnused(
  project,
  version,
  fetchImplementation = globalThis.fetch,
) {
  const projectName = requireString(project, "PyPI project");
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(projectName)) {
    fail(`invalid PyPI project '${projectName}'`);
  }
  requireString(version, "PyPI version");
  if (typeof fetchImplementation !== "function") {
    fail("a Fetch API implementation is required");
  }

  const url = `https://pypi.org/pypi/${encodeURIComponent(projectName)}/${encodeURIComponent(version)}/json`;
  const response = await fetchImplementation(url, {
    headers: { Accept: "application/json" },
    redirect: "error",
    cache: "no-store",
  });
  if (response.status === 404) {
    return Object.freeze({ project: projectName, version, unused: true });
  }
  if (response.status === 200) {
    fail(`${projectName} ${version} already exists on PyPI`);
  }
  fail(`PyPI version check failed with HTTP ${response.status}`);
}

export async function assertPypiVersionPublished(
  project,
  version,
  artifacts,
  fetchImplementation = globalThis.fetch,
) {
  const projectName = requireString(project, "PyPI project");
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(projectName)) {
    fail(`invalid PyPI project '${projectName}'`);
  }
  requireString(version, "PyPI version");
  if (typeof fetchImplementation !== "function") {
    fail("a Fetch API implementation is required");
  }
  if (!artifacts || typeof artifacts !== "object") {
    fail("validated local artifacts are required");
  }

  const url = `https://pypi.org/pypi/${encodeURIComponent(projectName)}/${encodeURIComponent(version)}/json`;
  const response = await fetchImplementation(url, {
    headers: { Accept: "application/json" },
    redirect: "error",
    cache: "no-store",
  });
  if (response.status === 404) {
    fail(`${projectName} ${version} is not published on PyPI`);
  }
  if (!response.ok) {
    await responseError(response, "PyPI published-version check");
  }
  const payload = await response.json();
  if (!payload || !Array.isArray(payload.urls)) {
    fail("PyPI published-version response is missing distribution files");
  }

  const expectedFiles = new Map([
    [
      artifacts.wheelName,
      { digest: artifacts.wheelDigest, size: artifacts.wheelSize },
    ],
    [
      artifacts.sdistName,
      { digest: artifacts.sdistDigest, size: artifacts.sdistSize },
    ],
  ]);
  const seen = new Set();
  for (const file of payload.urls) {
    if (!file || typeof file.filename !== "string") {
      fail(
        "PyPI published-version response contains a file without a valid filename",
      );
    }
    if (seen.has(file.filename)) {
      fail(`PyPI contains duplicate distribution '${file.filename}'`);
    }
    seen.add(file.filename);
    const expected = expectedFiles.get(file.filename);
    if (!expected) {
      fail(`PyPI contains unexpected distribution '${file.filename}'`);
    }
    const digest = file.digests?.sha256;
    if (`sha256:${digest}` !== expected.digest) {
      fail(
        `PyPI distribution '${file.filename}' does not match the local SHA-256 digest`,
      );
    }
    if (file.size !== expected.size) {
      fail(
        `PyPI distribution '${file.filename}' has size ${file.size}, expected ${expected.size}`,
      );
    }
  }
  for (const filename of expectedFiles.keys()) {
    if (!seen.has(filename)) {
      fail(`PyPI is missing expected distribution '${filename}'`);
    }
  }
  return Object.freeze({ project: projectName, version, published: true });
}

export async function assertGitHubIdentity(
  expectedLogin,
  token,
  fetchImplementation = globalThis.fetch,
) {
  const expected = requireString(expectedLogin, "expected GitHub login");
  if (!/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(expected)) {
    fail(`invalid expected GitHub login '${expected}'`);
  }
  const authToken = requireString(token, "GitHub token");
  if (typeof fetchImplementation !== "function") {
    fail("a Fetch API implementation is required");
  }
  const response = await fetchImplementation("https://api.github.com/user", {
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${authToken}`,
      "X-GitHub-Api-Version": "2022-11-28",
    },
    redirect: "error",
    cache: "no-store",
  });
  if (!response.ok) {
    await responseError(response, "GitHub identity check");
  }
  const payload = await response.json();
  if (!payload || payload.login !== expected) {
    fail(
      `GitHub token authenticates as '${payload?.login ?? "unknown"}', expected '${expected}'`,
    );
  }
  return Object.freeze({ login: expected, verified: true });
}

function parseArguments(argv) {
  if (argv.length === 0) {
    fail("a release-tools subcommand is required");
  }
  const command = argv[0];
  const options = {};
  for (let index = 1; index < argv.length; index += 2) {
    const name = argv[index];
    const value = argv[index + 1];
    if (!name?.startsWith("--") || value === undefined) {
      fail(`malformed argument list near '${name ?? "end of input"}'`);
    }
    const key = name.slice(2);
    if (!/^[a-z][a-z0-9-]*$/.test(key) || Object.hasOwn(options, key)) {
      fail(`invalid or duplicate option '${name}'`);
    }
    options[key] = value;
  }
  return { command, options };
}

function requireOptions(options, required, optional = []) {
  const allowed = new Set([...required, ...optional]);
  for (const name of Object.keys(options)) {
    if (!allowed.has(name)) {
      fail(`unexpected option '--${name}'`);
    }
  }
  for (const name of required) {
    if (!Object.hasOwn(options, name)) {
      fail(`missing required option '--${name}'`);
    }
  }
}

function parseBooleanOption(value, label) {
  if (value === undefined) {
    return false;
  }
  if (value !== "true" && value !== "false") {
    fail(`${label} must be 'true' or 'false'`);
  }
  return value === "true";
}

function parseIntegerOption(value, label, fallback) {
  if (value === undefined) {
    return fallback;
  }
  if (!/^(0|[1-9][0-9]*)$/.test(value)) {
    fail(`${label} must be a non-negative integer`);
  }
  return Number(value);
}

function emitResult(result, outputs, outputPath) {
  if (outputPath) {
    writeGitHubOutputs(outputPath, outputs);
  }
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function runCli(argv) {
  const { command, options } = parseArguments(argv);
  const defaultOutput = options["github-output"] ?? process.env.GITHUB_OUTPUT;

  if (command === "help" || command === "--help") {
    requireOptions(options, []);
    process.stdout.write(CLI_USAGE);
    return;
  }

  if (command === "derive") {
    requireOptions(options, ["channel", "version"], ["github-output"]);
    const release = deriveRelease(options.channel, options.version);
    emitResult(
      release,
      {
        version: release.version,
        tag: release.tag,
        title: release.title,
        distribution: release.distribution,
        normalized_distribution: release.normalizedDistribution,
        prerelease: release.isPrerelease,
        latest: !release.isPrerelease,
        version_branch: release.versionBranch,
        wheel_name: release.wheelName,
        sdist_name: release.sdistName,
      },
      defaultOutput,
    );
    return;
  }

  if (command === "update-changelog") {
    requireOptions(
      options,
      ["path", "version", "previous-tag", "branch", "repository"],
      ["previous-final-tag", "date"],
    );
    const result = updateChangelogFile({
      path: options.path,
      version: options.version,
      previousTag: options["previous-tag"],
      previousFinalTag: options["previous-final-tag"] ?? null,
      branch: options.branch,
      repository: options.repository,
      date: options.date ?? new Date().toISOString().slice(0, 10),
    });
    emitResult(result, {}, null);
    return;
  }

  if (command === "release-history") {
    requireOptions(options, ["repository", "version"], ["github-output"]);
    const history = readReleaseHistory(options.repository, options.version);
    emitResult(
      history,
      {
        previous_tag: history.previousTag,
        previous_final_tag: history.previousFinalTag,
      },
      defaultOutput,
    );
    return;
  }

  if (command === "check-changelog") {
    requireOptions(options, ["path", "version", "repository"]);
    const changelogPath = resolve(
      requireString(options.path, "changelog path"),
    );
    if (!existsSync(changelogPath) || !lstatSync(changelogPath).isFile()) {
      fail(`changelog not found at '${changelogPath}'`);
    }
    emitResult(
      assertChangelogPreparedText(
        readFileSync(changelogPath, "utf8"),
        options.version,
        options.repository,
      ),
      {},
      null,
    );
    return;
  }

  if (command === "rtd-release") {
    requireOptions(
      options,
      ["version"],
      ["project", "sync", "dry-run", "token-env", "attempts", "retry-delay-ms"],
    );
    const tokenEnvironment = options["token-env"] ?? "READTHEDOCS_TOKEN";
    if (!OUTPUT_NAME_PATTERN.test(tokenEnvironment)) {
      fail(`invalid token environment variable '${tokenEnvironment}'`);
    }
    const result = await manageReadTheDocsRelease({
      project: options.project ?? "pycord",
      version: options.version,
      token: process.env[tokenEnvironment] ?? null,
      sync: parseBooleanOption(options.sync, "--sync"),
      dryRun: parseBooleanOption(options["dry-run"], "--dry-run"),
      attempts: parseIntegerOption(options.attempts, "--attempts", 12),
      retryDelayMs: parseIntegerOption(
        options["retry-delay-ms"],
        "--retry-delay-ms",
        5_000,
      ),
    });
    emitResult(result, {}, null);
    return;
  }

  if (command === "notify-discord") {
    requireOptions(
      options,
      ["version", "previous-tag", "repository"],
      ["previous-final-tag", "dry-run", "webhook-env"],
    );
    const webhookEnvironment = options["webhook-env"] ?? "DISCORD_WEBHOOK_URL";
    if (!OUTPUT_NAME_PATTERN.test(webhookEnvironment)) {
      fail(`invalid webhook environment variable '${webhookEnvironment}'`);
    }
    const result = await sendDiscordReleaseNotification({
      version: options.version,
      previousTag: options["previous-tag"],
      previousFinalTag: options["previous-final-tag"] ?? null,
      repository: options.repository,
      webhookUrl: process.env[webhookEnvironment] ?? null,
      dryRun: parseBooleanOption(options["dry-run"], "--dry-run"),
    });
    emitResult(result, {}, null);
    return;
  }

  if (command === "prepare-dev-source") {
    requireOptions(options, ["source", "destination"], ["github-output"]);
    const prepared = prepareDevSource(options.source, options.destination);
    emitResult(prepared, { source_dir: prepared.destination }, defaultOutput);
    return;
  }

  if (command === "source-date-epoch") {
    requireOptions(options, ["repository", "commit"], ["github-output"]);
    const epoch = deriveSourceDateEpoch(options.repository, options.commit);
    emitResult(
      { sourceDateEpoch: epoch },
      { source_date_epoch: epoch },
      defaultOutput,
    );
    return;
  }

  if (command === "validate-artifacts") {
    requireOptions(
      options,
      ["channel", "version", "dist-dir"],
      ["github-output"],
    );
    const artifacts = validateArtifacts(
      options.channel,
      options.version,
      options["dist-dir"],
    );
    emitResult(
      artifacts,
      {
        dist_dir: artifacts.distDir,
        wheel_name: artifacts.wheelName,
        wheel_path: artifacts.wheelPath,
        wheel_digest: artifacts.wheelDigest,
        sdist_name: artifacts.sdistName,
        sdist_path: artifacts.sdistPath,
        sdist_digest: artifacts.sdistDigest,
      },
      defaultOutput,
    );
    return;
  }

  if (command === "stage-artifacts") {
    requireOptions(
      options,
      ["channel", "version", "source-dir", "destination"],
      ["github-output"],
    );
    const artifacts = stageArtifacts(
      options.channel,
      options.version,
      options["source-dir"],
      options.destination,
    );
    emitResult(
      artifacts,
      {
        dist_dir: artifacts.distDir,
        wheel_name: artifacts.wheelName,
        wheel_path: artifacts.wheelPath,
        wheel_digest: artifacts.wheelDigest,
        sdist_name: artifacts.sdistName,
        sdist_path: artifacts.sdistPath,
        sdist_digest: artifacts.sdistDigest,
      },
      defaultOutput,
    );
    return;
  }

  if (command === "check-tag") {
    requireOptions(
      options,
      ["repository", "remote", "tag", "expected-commit"],
      ["github-output", "require-existing"],
    );
    const state = readRemoteTagState(
      options.repository,
      options.remote,
      options.tag,
      options["expected-commit"],
    );
    if (state.state === "conflicting") {
      fail(`tag '${options.tag}' conflicts: ${state.reason}`);
    }
    if (
      parseBooleanOption(options["require-existing"], "--require-existing") &&
      state.state !== "reusable"
    ) {
      fail(
        `tag '${options.tag}' must already exist and target ${options["expected-commit"]}`,
      );
    }
    emitResult(
      state,
      { tag_state: state.state, create_tag: state.createTag },
      defaultOutput,
    );
    return;
  }

  if (command === "resolve-tag") {
    requireOptions(options, ["repository", "remote", "tag"], ["github-output"]);
    const state = resolveRemoteAnnotatedTag(
      options.repository,
      options.remote,
      options.tag,
    );
    emitResult(
      state,
      { tag_state: "reusable", tag_commit: state.commit },
      defaultOutput,
    );
    return;
  }

  if (command === "check-release") {
    requireOptions(
      options,
      ["channel", "version", "expected-commit", "dist-dir", "state-file"],
      ["github-output"],
    );
    const derived = deriveRelease(options.channel, options.version);
    const artifacts = validateArtifacts(
      options.channel,
      options.version,
      options["dist-dir"],
    );
    const payload = JSON.parse(readFileSync(options["state-file"], "utf8"));
    const state = classifyReleaseState(
      payload,
      {
        tag: derived.tag,
        title: derived.title,
        commit: options["expected-commit"],
        isPrerelease: derived.isPrerelease,
      },
      artifacts,
    );
    emitResult(
      state,
      {
        release_state: state.state,
        create_release: state.createRelease,
        resume_draft: state.resumeDraft,
        reuse_release: state.reuseRelease,
        wheel_missing: state.wheelMissing,
        sdist_missing: state.sdistMissing,
      },
      defaultOutput,
    );
    return;
  }

  if (command === "check-github-release") {
    requireOptions(
      options,
      [
        "channel",
        "version",
        "expected-commit",
        "dist-dir",
        "repository",
        "tag-state",
      ],
      ["github-output", "token-env"],
    );
    const tokenEnvironment = options["token-env"] ?? "GITHUB_TOKEN";
    if (!OUTPUT_NAME_PATTERN.test(tokenEnvironment)) {
      fail(`invalid token environment variable '${tokenEnvironment}'`);
    }
    const derived = deriveRelease(options.channel, options.version);
    const artifacts = validateArtifacts(
      options.channel,
      options.version,
      options["dist-dir"],
    );
    const payload = await fetchGitHubReleaseState(
      options.repository,
      derived.tag,
      process.env[tokenEnvironment] ?? null,
    );
    const state = classifyReleaseState(
      payload,
      {
        tag: derived.tag,
        title: derived.title,
        commit: options["expected-commit"],
        tagState: options["tag-state"],
        isPrerelease: derived.isPrerelease,
      },
      artifacts,
    );
    emitResult(
      state,
      {
        release_state: state.state,
        create_release: state.createRelease,
        resume_draft: state.resumeDraft,
        reuse_release: state.reuseRelease,
        wheel_missing: state.wheelMissing,
        sdist_missing: state.sdistMissing,
      },
      defaultOutput,
    );
    return;
  }

  if (command === "check-immutable") {
    requireOptions(options, ["state-file"]);
    const payload = JSON.parse(readFileSync(options["state-file"], "utf8"));
    emitResult(assertImmutableReleaseSetting(payload), {}, null);
    return;
  }

  if (command === "check-pypi-unused") {
    requireOptions(options, ["project", "version"]);
    emitResult(
      await assertPypiVersionUnused(options.project, options.version),
      {},
      null,
    );
    return;
  }

  if (command === "check-pypi-published") {
    requireOptions(options, ["project", "version", "channel", "dist-dir"]);
    const artifacts = validateArtifacts(
      options.channel,
      options.version,
      options["dist-dir"],
    );
    emitResult(
      await assertPypiVersionPublished(
        options.project,
        options.version,
        artifacts,
      ),
      {},
      null,
    );
    return;
  }

  if (command === "check-github-identity") {
    requireOptions(options, ["expected-login"], ["token-env"]);
    const tokenEnvironment = options["token-env"] ?? "GITHUB_TOKEN";
    if (!OUTPUT_NAME_PATTERN.test(tokenEnvironment)) {
      fail(`invalid token environment variable '${tokenEnvironment}'`);
    }
    emitResult(
      await assertGitHubIdentity(
        options["expected-login"],
        process.env[tokenEnvironment] ?? null,
      ),
      {},
      null,
    );
    return;
  }

  if (command === "milestone-candidates") {
    requireOptions(options, ["version"], ["github-output"]);
    const candidates = milestoneTitleCandidates(options.version);
    emitResult(
      { candidates },
      { milestone_candidates: candidates },
      defaultOutput,
    );
    return;
  }

  if (command === "close-milestone") {
    requireOptions(
      options,
      ["repository", "version"],
      ["dry-run", "token-env"],
    );
    const tokenEnvironment = options["token-env"] ?? "GITHUB_TOKEN";
    if (!OUTPUT_NAME_PATTERN.test(tokenEnvironment)) {
      fail(`invalid token environment variable '${tokenEnvironment}'`);
    }
    const result = await closeReleaseMilestone({
      repository: options.repository,
      version: options.version,
      token: process.env[tokenEnvironment] ?? null,
      dryRun: parseBooleanOption(options["dry-run"], "--dry-run"),
    });
    emitResult(result, {}, null);
    return;
  }

  fail(`unknown release-tools subcommand '${command}'`);
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : null;
if (invokedPath && invokedPath === fileURLToPath(import.meta.url)) {
  try {
    await runCli(process.argv.slice(2));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(
      `release-tools: ${message.replace(/[\r\n]+/g, " ")}\n`,
    );
    process.exitCode = 1;
  }
}
