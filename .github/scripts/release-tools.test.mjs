import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, test } from "node:test";

import {
  assertChangelogPreparedText,
  assertGitHubIdentity,
  assertImmutableReleaseSetting,
  assertPypiVersionPublished,
  assertPypiVersionUnused,
  buildDiscordReleaseMessage,
  buildDiscordReleasePayload,
  buildUnreleasedChangelogBlock,
  closeReleaseMilestone,
  classifyMilestoneState,
  classifyReleaseState,
  classifyTagState,
  deriveReadTheDocsRelease,
  deriveRelease,
  deriveReleaseHistory,
  fetchGitHubReleaseState,
  formatGitHubOutputs,
  manageReadTheDocsRelease,
  milestoneTitleCandidates,
  parseChangelogCategories,
  parseReleaseVersion,
  parseSourceDateEpoch,
  prepareDevSource,
  renderChangelogReleaseBody,
  resolveAnnotatedTagState,
  rewriteProjectNameText,
  sendDiscordReleaseNotification,
  stageArtifacts,
  updateChangelogText,
  validateArtifacts,
  writeGitHubOutputs,
} from "./release-tools.mjs";

const temporaryDirectories = [];

function temporaryDirectory() {
  const directory = mkdtempSync(join(tmpdir(), "pycord-release-tools-"));
  temporaryDirectories.push(directory);
  return directory;
}

function createSourceFixture() {
  const root = temporaryDirectory();
  writeFileSync(
    join(root, "pyproject.toml"),
    '[build-system]\nrequires = ["hatchling"]\n\n[project]\nname = "py-cord"\ndynamic = ["version"]\n',
  );
  mkdirSync(join(root, "discord"));
  writeFileSync(join(root, "discord", "__init__.py"), "__version__ = 'test'\n");
  writeFileSync(join(root, "untracked.txt"), "must not be copied\n");
  return root;
}

function createArtifacts(channel = "dev", version = "2.8.2.dev1") {
  const directory = temporaryDirectory();
  const release = deriveRelease(channel, version);
  writeFileSync(join(directory, release.wheelName), "wheel-content");
  writeFileSync(join(directory, release.sdistName), "sdist-content");
  return validateArtifacts(channel, version, directory);
}

function releaseAsset(name, digest, size) {
  return { name, digest, size };
}

function matchingReleasePayload(artifacts, overrides = {}) {
  return {
    tag_name: "dev-v2.8.2.dev1",
    name: "Pycord Development 2.8.2.dev1",
    draft: false,
    immutable: true,
    prerelease: true,
    target_commitish: "a".repeat(40),
    assets: [
      releaseAsset(artifacts.wheelName, artifacts.wheelDigest, artifacts.wheelSize),
      releaseAsset(artifacts.sdistName, artifacts.sdistDigest, artifacts.sdistSize),
    ],
    ...overrides,
  };
}

function response(status, body = "") {
  return {
    ok: status >= 200 && status < 300,
    status,
    async text() {
      return body;
    },
  };
}

function jsonResponse(status, payload) {
  return {
    ...response(status, JSON.stringify(payload)),
    async json() {
      return payload;
    },
  };
}

afterEach(() => {
  while (temporaryDirectories.length > 0) {
    rmSync(temporaryDirectories.pop(), { recursive: true, force: true });
  }
});

test("accepts canonical development versions", () => {
  for (const version of ["0.0.0.dev0", "2.8.2.dev1", "10.20.30.dev456"]) {
    assert.equal(parseReleaseVersion("dev", version).version, version);
  }
});

test("accepts canonical production final and release candidate versions", () => {
  assert.equal(parseReleaseVersion("production", "2.9.0").isPrerelease, false);
  assert.equal(parseReleaseVersion("production", "2.9.0rc1").isPrerelease, true);
});

test("rejects malformed, noncanonical, and hostile versions", () => {
  const rejected = [
    "2.8.2",
    "2.8.2rc1",
    "2.8.2.dev",
    "2.8.2.dev01",
    "02.8.2.dev1",
    "2.8.2.dev1 ",
    " 2.8.2.dev1",
    "2.8.2.dev1+local",
    "2.8.2.dev1; echo bad",
    "$(whoami)",
    "2.8.2-dev1",
  ];
  for (const version of rejected) {
    assert.throws(() => parseReleaseVersion("dev", version));
  }
  for (const version of ["2.9.0.dev1", "2.9.0rc.1", "2.9", "v2.9.0", "2.9.0+local"]) {
    assert.throws(() => parseReleaseVersion("production", version));
  }
});

test("derives development release values", () => {
  assert.deepEqual(
    deriveRelease("dev", "2.8.2.dev1"),
    {
      channel: "dev",
      version: "2.8.2.dev1",
      major: 2,
      minor: 8,
      patch: 2,
      prereleaseNumber: 1,
      isPrerelease: true,
      distribution: "py-cord-dev",
      normalizedDistribution: "py_cord_dev",
      tag: "dev-v2.8.2.dev1",
      title: "Pycord Development 2.8.2.dev1",
      versionBranch: null,
      wheelName: "py_cord_dev-2.8.2.dev1-py3-none-any.whl",
      sdistName: "py_cord_dev-2.8.2.dev1.tar.gz",
    },
  );
});

test("derives future production branch, tag, artifacts, and prerelease state", () => {
  const release = deriveRelease("production", "2.9.0rc1");
  assert.equal(release.tag, "v2.9.0rc1");
  assert.equal(release.title, "v2.9.0rc1");
  assert.equal(release.versionBranch, "v2.9.x");
  assert.equal(release.wheelName, "py_cord-2.9.0rc1-py3-none-any.whl");
  assert.equal(release.isPrerelease, true);
});

test("rewrites only the project name", () => {
  const before =
    '[project]\nname = "py-cord" # distribution\ndescription = "py-cord remains here"\n\n[project.urls]\nname = "unchanged"\n';
  const after = rewriteProjectNameText(before);
  assert.equal(
    after,
    '[project]\nname = "py-cord-dev" # distribution\ndescription = "py-cord remains here"\n\n[project.urls]\nname = "unchanged"\n',
  );
});

test("rejects missing, duplicate, or unexpected project names", () => {
  assert.throws(() => rewriteProjectNameText('[project]\ndescription = "missing"\n'), /assignment, found 0/);
  assert.throws(
    () => rewriteProjectNameText('[project]\nname = "py-cord"\nname = "py-cord"\n'),
    /assignment, found 2/,
  );
  assert.throws(() => rewriteProjectNameText('[project]\nname = "py-cord-dev"\n'), /must be exactly/);
  assert.throws(
    () => rewriteProjectNameText('[project]\nname = "py-cord"\n\n[project]\nname = "py-cord"\n'),
    /one \[project] table/,
  );
});

test("copies only declared tracked files into an isolated development source", () => {
  const source = createSourceFixture();
  const destination = join(temporaryDirectory(), "prepared");
  const result = prepareDevSource(source, destination, {
    trackedFiles: ["pyproject.toml", "discord/__init__.py"],
  });
  assert.equal(result.fileCount, 2);
  assert.match(readFileSync(join(destination, "pyproject.toml"), "utf8"), /name = "py-cord-dev"/);
  assert.equal(readFileSync(join(destination, "discord", "__init__.py"), "utf8"), "__version__ = 'test'\n");
  assert.throws(() => readFileSync(join(destination, "untracked.txt")));
  assert.match(readFileSync(join(source, "pyproject.toml"), "utf8"), /name = "py-cord"/);
});

test("accepts only canonical source date epochs", () => {
  assert.equal(parseSourceDateEpoch("1724414400\n"), "1724414400");
  for (const value of ["", "-1", "01", "1.5", "$(date)"]) {
    assert.throws(() => parseSourceDateEpoch(value));
  }
});

test("rejects source and destination overlap", () => {
  const source = createSourceFixture();
  assert.throws(
    () => prepareDevSource(source, join(source, "prepared"), { trackedFiles: ["pyproject.toml"] }),
    /must not overlap/,
  );
});

test("rejects tracked path traversal", () => {
  const source = createSourceFixture();
  const destination = join(temporaryDirectory(), "prepared");
  assert.throws(
    () => prepareDevSource(source, destination, { trackedFiles: ["pyproject.toml", "../secret.txt"] }),
    /unsafe component/,
  );
});

test("rejects tracked paths that escape through a directory symlink", () => {
  const source = createSourceFixture();
  const outside = temporaryDirectory();
  writeFileSync(join(outside, "secret.txt"), "secret");
  const link = join(source, "linked");
  symlinkSync(outside, link, process.platform === "win32" ? "junction" : "dir");
  const destination = join(temporaryDirectory(), "prepared");
  assert.throws(
    () => prepareDevSource(source, destination, { trackedFiles: ["pyproject.toml", "linked/secret.txt"] }),
    /resolves outside/,
  );
});

test("accepts exactly the expected wheel and sdist", () => {
  const artifacts = createArtifacts();
  assert.equal(artifacts.wheelName, "py_cord_dev-2.8.2.dev1-py3-none-any.whl");
  assert.equal(artifacts.sdistName, "py_cord_dev-2.8.2.dev1.tar.gz");
  assert.match(artifacts.wheelDigest, /^sha256:[0-9a-f]{64}$/);
});

test("stages only validated artifacts and preserves their digests", () => {
  const source = createArtifacts();
  const destination = join(temporaryDirectory(), "dist-dev");
  const staged = stageArtifacts("dev", "2.8.2.dev1", source.distDir, destination);
  assert.equal(staged.wheelDigest, source.wheelDigest);
  assert.equal(staged.sdistDigest, source.sdistDigest);
  assert.throws(
    () => stageArtifacts("dev", "2.8.2.dev1", source.distDir, destination),
    /already exists/,
  );
});

test("rejects missing, wrong, duplicate-equivalent, and extra distributions", () => {
  const directory = temporaryDirectory();
  writeFileSync(join(directory, "py_cord_dev-2.8.2.dev1-py3-none-any.whl"), "wheel");
  assert.throws(() => validateArtifacts("dev", "2.8.2.dev1", directory), /expected exactly/);
  writeFileSync(join(directory, "py_cord_dev-2.8.2.dev1.tar.gz"), "sdist");
  writeFileSync(join(directory, "py_cord_dev-2.8.2.dev1.zip"), "extra");
  assert.throws(() => validateArtifacts("dev", "2.8.2.dev1", directory), /expected exactly/);
  rmSync(join(directory, "py_cord_dev-2.8.2.dev1.zip"));
  rmSync(join(directory, "py_cord_dev-2.8.2.dev1.tar.gz"));
  writeFileSync(join(directory, "py_cord_dev-2.8.2.dev2.tar.gz"), "wrong version");
  assert.throws(() => validateArtifacts("dev", "2.8.2.dev1", directory), /expected exactly/);
});

test("classifies absent, reusable annotated, lightweight, and conflicting tags", () => {
  const tag = "dev-v2.8.2.dev1";
  const expected = "a".repeat(40);
  assert.equal(classifyTagState(tag, expected, []).state, "absent");
  assert.equal(
    classifyTagState(tag, expected, [
      { ref: `refs/tags/${tag}`, sha: "b".repeat(40) },
      { ref: `refs/tags/${tag}^{}`, sha: expected },
    ]).state,
    "reusable",
  );
  assert.match(
    classifyTagState(tag, expected, [{ ref: `refs/tags/${tag}`, sha: expected }]).reason,
    /lightweight/,
  );
  assert.match(
    classifyTagState(tag, expected, [
      { ref: `refs/tags/${tag}`, sha: "b".repeat(40) },
      { ref: `refs/tags/${tag}^{}`, sha: "c".repeat(40) },
    ]).reason,
    /targets/,
  );
  assert.throws(() => classifyTagState("dev-v2.8.2.dev1;bad", expected, []), /invalid Git tag/);
});

test("resolves only a single annotated tag and exposes its peeled commit", () => {
  const tag = "v2.9.0";
  const commit = "a".repeat(40);
  assert.equal(resolveAnnotatedTagState(tag, []).state, "absent");
  assert.deepEqual(
    resolveAnnotatedTagState(tag, [
      { ref: `refs/tags/${tag}`, sha: "b".repeat(40) },
      { ref: `refs/tags/${tag}^{}`, sha: commit },
    ]),
    { state: "annotated", commit },
  );
  assert.throws(
    () => resolveAnnotatedTagState(tag, [{ ref: `refs/tags/${tag}`, sha: commit }]),
    /annotated tag/,
  );
});

test("derives ordered production history while ignoring noncanonical tags", () => {
  assert.deepEqual(
    deriveReleaseHistory("2.9.0", ["v2.8.1", "v2.9.0rc1", "v2.9.0rc2", "v2.9.0rc.3", "dev-v2.9.0.dev1"]),
    { previousTag: "v2.9.0rc2", previousFinalTag: "v2.8.1" },
  );
  assert.deepEqual(
    deriveReleaseHistory("2.9.0rc1", ["v2.8.0", "v2.8.1", "v2.9.0"]),
    { previousTag: "v2.8.1", previousFinalTag: "v2.8.1" },
  );
  assert.throws(() => deriveReleaseHistory("1.0.0", ["v1.0.0rc1"]), /previous production tags/);
});

test("classifies an absent release", () => {
  const artifacts = createArtifacts();
  const state = classifyReleaseState(
    null,
    { tag: "dev-v2.8.2.dev1", title: "Pycord Development 2.8.2.dev1", commit: "a".repeat(40) },
    artifacts,
  );
  assert.equal(state.state, "absent");
  assert.equal(state.createRelease, true);
});

test("classifies a matching resumable draft and identifies missing assets", () => {
  const artifacts = createArtifacts();
  const payload = matchingReleasePayload(artifacts, {
    draft: true,
    immutable: false,
    assets: [releaseAsset(artifacts.wheelName, artifacts.wheelDigest, artifacts.wheelSize)],
  });
  const state = classifyReleaseState(
    payload,
    { tag: payload.tag_name, title: payload.name, commit: payload.target_commitish },
    artifacts,
  );
  assert.equal(state.state, "draft");
  assert.equal(state.wheelMissing, false);
  assert.equal(state.sdistMissing, true);
});

test("classifies a matching immutable published release", () => {
  const artifacts = createArtifacts();
  const payload = matchingReleasePayload(artifacts);
  const state = classifyReleaseState(
    payload,
    { tag: payload.tag_name, title: payload.name, commit: payload.target_commitish },
    artifacts,
  );
  assert.equal(state.state, "published");
  assert.equal(state.reuseRelease, true);
});

test("classifies final production releases as non-prereleases", () => {
  const artifacts = createArtifacts("production", "2.9.0");
  const payload = {
    tag_name: "v2.9.0",
    name: "v2.9.0",
    draft: false,
    immutable: true,
    prerelease: false,
    target_commitish: "a".repeat(40),
    assets: [
      releaseAsset(artifacts.wheelName, artifacts.wheelDigest, artifacts.wheelSize),
      releaseAsset(artifacts.sdistName, artifacts.sdistDigest, artifacts.sdistSize),
    ],
  };
  assert.equal(
    classifyReleaseState(
      payload,
      {
        tag: payload.tag_name,
        title: payload.name,
        commit: payload.target_commitish,
        isPrerelease: false,
      },
      artifacts,
    ).state,
    "published",
  );
  assert.throws(
    () =>
      classifyReleaseState(
        { ...payload, prerelease: true },
        {
          tag: payload.tag_name,
          title: payload.name,
          commit: payload.target_commitish,
          isPrerelease: false,
        },
        artifacts,
      ),
    /isPrerelease/,
  );
});

test("rejects mismatched release metadata, mutable publication, assets, and digests", () => {
  const artifacts = createArtifacts();
  const expected = {
    tag: "dev-v2.8.2.dev1",
    title: "Pycord Development 2.8.2.dev1",
    commit: "a".repeat(40),
  };
  assert.throws(
    () => classifyReleaseState(matchingReleasePayload(artifacts, { name: "wrong" }), expected, artifacts),
    /title/,
  );
  assert.throws(
    () => classifyReleaseState(matchingReleasePayload(artifacts, { immutable: false }), expected, artifacts),
    /must be immutable/,
  );
  assert.throws(
    () =>
      classifyReleaseState(
        matchingReleasePayload(artifacts, {
          assets: [
            releaseAsset(artifacts.wheelName, artifacts.wheelDigest, artifacts.wheelSize),
            releaseAsset("unexpected.txt", `sha256:${"0".repeat(64)}`, 1),
          ],
        }),
        expected,
        artifacts,
      ),
    /unexpected asset/,
  );
  assert.throws(
    () =>
      classifyReleaseState(
        matchingReleasePayload(artifacts, {
          assets: [
            releaseAsset(artifacts.wheelName, `sha256:${"0".repeat(64)}`, artifacts.wheelSize),
            releaseAsset(artifacts.sdistName, artifacts.sdistDigest, artifacts.sdistSize),
          ],
        }),
        expected,
        artifacts,
      ),
    /digest/,
  );
});

test("requires an existing release to have a reusable annotated tag", () => {
  const artifacts = createArtifacts();
  const payload = matchingReleasePayload(artifacts);
  assert.throws(
    () =>
      classifyReleaseState(
        payload,
        {
          tag: payload.tag_name,
          title: payload.name,
          commit: payload.target_commitish,
          tagState: "absent",
        },
        artifacts,
      ),
    /requires a reusable annotated tag/,
  );
});

test("fetches GitHub release state and treats only 404 as absent", async () => {
  let request;
  const payload = { tag_name: "dev-v2.8.2.dev1" };
  const found = await fetchGitHubReleaseState(
    "Pycord-Development/pycord",
    "dev-v2.8.2.dev1",
    "token",
    async (url, options) => {
      request = { url, options };
      return { ...response(200), async json() { return payload; } };
    },
  );
  assert.deepEqual(found, payload);
  assert.match(request.url, /releases\/tags\/dev-v2\.8\.2\.dev1$/);
  assert.equal(request.options.headers.Authorization, "Bearer token");
  assert.equal(
    await fetchGitHubReleaseState(
      "Pycord-Development/pycord",
      "dev-v2.8.2.dev1",
      "token",
      async () => response(404),
    ),
    null,
  );
  await assert.rejects(
    fetchGitHubReleaseState(
      "Pycord-Development/pycord",
      "dev-v2.8.2.dev1",
      "token",
      async () => response(500),
    ),
    /HTTP 500/,
  );
});

test("requires immutable releases to be enabled", () => {
  assert.deepEqual(assertImmutableReleaseSetting({ enabled: true, enforced_by_owner: false }), {
    enabled: true,
    enforcedByOwner: false,
  });
  assert.throws(() => assertImmutableReleaseSetting({ enabled: false }), /must be enabled/);
});

test("treats only a PyPI 404 as an unused version", async () => {
  assert.equal(
    (await assertPypiVersionUnused("py-cord-dev", "2.8.2.dev1", async () => response(404))).unused,
    true,
  );
  await assert.rejects(
    assertPypiVersionUnused("py-cord-dev", "2.8.2.dev1", async () => response(200)),
    /already exists/,
  );
  await assert.rejects(
    assertPypiVersionUnused("py-cord-dev", "2.8.2.dev1", async () => response(503)),
    /HTTP 503/,
  );
});

test("matches a published PyPI version to the exact local artifacts", async () => {
  const artifacts = createArtifacts("production", "2.9.0");
  const urls = [artifacts.wheelName, artifacts.sdistName].map((filename) => {
    const wheel = filename === artifacts.wheelName;
    return {
      filename,
      size: wheel ? artifacts.wheelSize : artifacts.sdistSize,
      digests: { sha256: (wheel ? artifacts.wheelDigest : artifacts.sdistDigest).slice(7) },
    };
  });
  const result = await assertPypiVersionPublished(
    "py-cord",
    "2.9.0",
    artifacts,
    async () => jsonResponse(200, { urls }),
  );
  assert.equal(result.published, true);
  await assert.rejects(
    assertPypiVersionPublished(
      "py-cord",
      "2.9.0",
      artifacts,
      async () => jsonResponse(200, { urls: urls.slice(0, 1) }),
    ),
    /missing expected distribution/,
  );
  await assert.rejects(
    assertPypiVersionPublished(
      "py-cord",
      "2.9.0",
      artifacts,
      async () => jsonResponse(200, { urls: [{ ...urls[0], digests: { sha256: "0".repeat(64) } }, urls[1]] }),
    ),
    /SHA-256/,
  );
  await assert.rejects(
    assertPypiVersionPublished("py-cord", "2.9.0", artifacts, async () => response(404)),
    /not published/,
  );
});

test("requires the exact GitHub automation identity", async () => {
  let request;
  const result = await assertGitHubIdentity("NyuwBot", "token", async (url, options) => {
    request = { url, options };
    return jsonResponse(200, { login: "NyuwBot" });
  });
  assert.deepEqual(result, { login: "NyuwBot", verified: true });
  assert.equal(request.options.headers.Authorization, "Bearer token");
  await assert.rejects(
    assertGitHubIdentity("NyuwBot", "token", async () => jsonResponse(200, { login: "someone-else" })),
    /expected 'NyuwBot'/,
  );
  await assert.rejects(
    assertGitHubIdentity("NyuwBot", "token", async () => response(401)),
    /HTTP 401/,
  );
});

test("generates future production milestone candidates and rejects ambiguity", () => {
  assert.deepEqual(milestoneTitleCandidates("2.9.0"), ["2.9.0", "v2.9.0"]);
  assert.deepEqual(milestoneTitleCandidates("2.9.0rc1"), [
    "2.9.0rc1",
    "v2.9.0rc1",
    "2.9.0rc.1",
    "v2.9.0rc.1",
  ]);
  assert.equal(classifyMilestoneState("2.9.0", [{ title: "2.9.0" }]).state, "matched");
  assert.throws(
    () => classifyMilestoneState("2.9.0", [{ title: "2.9.0" }, { title: "v2.9.0" }]),
    /multiple milestones/,
  );
});

test("dry-runs an exact release milestone close without mutation", async () => {
  const calls = [];
  const result = await closeReleaseMilestone(
    {
      repository: "Pycord-Development/pycord",
      version: "2.9.0rc1",
      token: "token",
      dryRun: true,
    },
    async (url, options) => {
      calls.push({ url, options });
      return jsonResponse(200, [
        { number: 14, title: "2.9.0rc1", state: "open", open_issues: 35 },
        { number: 13, title: "2.9.0", state: "open", open_issues: 0 },
      ]);
    },
  );
  assert.deepEqual(result, {
    number: 14,
    title: "2.9.0rc1",
    openIssues: 35,
    alreadyClosed: false,
    dryRun: true,
    closed: false,
  });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].options.method, undefined);
});

test("closes the exact release milestone and verifies the response", async () => {
  const calls = [];
  const result = await closeReleaseMilestone(
    {
      repository: "Pycord-Development/pycord",
      version: "2.9.0rc1",
      token: "token",
    },
    async (url, options) => {
      calls.push({ url, options });
      if (options.method === "PATCH") {
        return jsonResponse(200, { number: 9, title: "v2.9.0rc.1", state: "closed" });
      }
      return jsonResponse(200, [
        { number: 9, title: "v2.9.0rc.1", state: "open", open_issues: 2 },
      ]);
    },
  );
  assert.equal(result.closed, true);
  assert.equal(result.title, "v2.9.0rc.1");
  assert.equal(calls.length, 2);
  assert.equal(calls[1].options.method, "PATCH");
  assert.deepEqual(JSON.parse(calls[1].options.body), { state: "closed" });
});

test("milestone closing is idempotent and rejects absent or ambiguous matches", async () => {
  const closed = await closeReleaseMilestone(
    { repository: "Pycord-Development/pycord", version: "2.9.0", token: "token" },
    async () => jsonResponse(200, [{ number: 13, title: "2.9.0", state: "closed", open_issues: 0 }]),
  );
  assert.equal(closed.alreadyClosed, true);
  await assert.rejects(
    closeReleaseMilestone(
      { repository: "Pycord-Development/pycord", version: "2.9.0", token: "token" },
      async () => jsonResponse(200, []),
    ),
    /no milestone matches/,
  );
  await assert.rejects(
    closeReleaseMilestone(
      { repository: "Pycord-Development/pycord", version: "2.9.0", token: "token" },
      async () =>
        jsonResponse(200, [
          { number: 13, title: "2.9.0", state: "open", open_issues: 0 },
          { number: 99, title: "v2.9.0", state: "open", open_issues: 0 },
        ]),
    ),
    /multiple milestones/,
  );
});

test("serializes safe multiline GitHub outputs", () => {
  const formatted = formatGitHubOutputs(
    { version: "2.8.2.dev1", notes: "line one\nline two" },
    (() => {
      let index = 0;
      return () => `delimiter_${index++}`;
    })(),
  );
  assert.equal(
    formatted,
    "version<<delimiter_0\n2.8.2.dev1\ndelimiter_0\nnotes<<delimiter_1\nline one\nline two\ndelimiter_1\n",
  );
  assert.throws(() => formatGitHubOutputs({ "bad-name": "value" }), /invalid GitHub output name/);
});

test("appends GitHub outputs without truncating earlier values", () => {
  const directory = temporaryDirectory();
  const output = join(directory, "output.txt");
  writeFileSync(output, "existing=value\n");
  writeGitHubOutputs(output, { next: "value" });
  assert.match(readFileSync(output, "utf8"), /^existing=value\nnext<</);
});

test("builds and parses changelog categories in stable order", () => {
  const block = buildUnreleasedChangelogBlock("master");
  assert.match(block, /`master` branch/);
  const categories = parseChangelogCategories("### Fixed\n\n- Fixed a thing\n\n### Added\n- Added a thing\n");
  assert.equal(
    renderChangelogReleaseBody(categories),
    "### Added\n\n- Added a thing\n\n### Fixed\n\n- Fixed a thing",
  );
});

test("updates a release changelog and merges matching RC entries into a final release", () => {
  const changelog = `# Changelog

## [Unreleased]

### Added

- Final addition

## [2.9.0rc1] - 2026-08-01
### Fixed

- RC fix

## [2.8.1] - 2026-07-25
### Changed

- Previous change

[unreleased]: https://github.com/Pycord-Development/pycord/compare/v2.9.0rc1...HEAD
[2.9.0rc1]: https://github.com/Pycord-Development/pycord/compare/v2.8.1...v2.9.0rc1
`;
  const updated = updateChangelogText({
    text: changelog,
    version: "2.9.0",
    previousTag: "v2.9.0rc1",
    previousFinalTag: "v2.8.1",
    branch: "master",
    repository: "Pycord-Development/pycord",
    date: "2026-08-23",
  });
  assert.match(updated, /^## \[2\.9\.0] - 2026-08-23$/m);
  assert.match(updated, /- Final addition/);
  assert.match(updated, /- RC fix/);
  assert.match(updated, /^\[2\.9\.0]: .*compare\/v2\.8\.1\.\.\.v2\.9\.0$/m);
  assert.match(updated, /^\[unreleased]: .*compare\/v2\.9\.0\.\.\.HEAD$/m);
  assert.deepEqual(
    assertChangelogPreparedText(updated, "2.9.0", "Pycord-Development/pycord"),
    { version: "2.9.0", prepared: true },
  );
  assert.throws(
    () =>
      updateChangelogText({
        text: updated,
        version: "2.9.0",
        previousTag: "v2.9.0rc1",
        previousFinalTag: "v2.8.1",
        branch: "master",
        repository: "Pycord-Development/pycord",
        date: "2026-08-23",
      }),
    /already contains/,
  );
});

test("rejects changelogs without an Unreleased section", () => {
  assert.throws(
    () =>
      updateChangelogText({
        text: "# Changelog\n",
        version: "2.9.0",
        previousTag: "v2.8.1",
        branch: "master",
        repository: "Pycord-Development/pycord",
        date: "2026-08-23",
      }),
    /missing.*Unreleased/i,
  );
});

test("derives stable and RC Read the Docs versions", () => {
  assert.deepEqual(deriveReadTheDocsRelease("2.9.0"), {
    version: "2.9.0",
    docsVersion: "v2.9.0",
    hidden: false,
  });
  assert.deepEqual(deriveReadTheDocsRelease("2.9.0rc1"), {
    version: "2.9.0rc1",
    docsVersion: "v2.9.x",
    hidden: true,
  });
});

test("Read the Docs dry run does not require a token", async () => {
  const result = await manageReadTheDocsRelease({ version: "2.9.0", sync: true, dryRun: true });
  assert.equal(result.docsVersion, "v2.9.0");
  assert.equal(result.sync, true);
});

test("Read the Docs sync waits for the version before activation", async () => {
  const calls = [];
  const statuses = [202, 404, 404, 200, 200];
  const result = await manageReadTheDocsRelease(
    { version: "2.9.0rc1", token: "token", sync: true, attempts: 3, retryDelayMs: 0 },
    {
      fetchImplementation: async (url, options) => {
        calls.push({ url, options });
        return response(statuses.shift());
      },
      delayImplementation: async () => {},
    },
  );
  assert.equal(result.docsVersion, "v2.9.x");
  assert.deepEqual(calls.map((call) => call.options.method), ["POST", "GET", "GET", "GET", "PATCH"]);
  assert.equal(JSON.parse(calls.at(-1).options.body).hidden, true);
});

test("Read the Docs sync fails when the version never appears", async () => {
  await assert.rejects(
    manageReadTheDocsRelease(
      { version: "2.9.0", token: "token", sync: true, attempts: 2, retryDelayMs: 0 },
      {
        fetchImplementation: async (url, options) => response(options.method === "POST" ? 202 : 404),
        delayImplementation: async () => {},
      },
    ),
    /did not appear/,
  );
});

test("builds Discord payloads for final and RC releases", () => {
  const finalMessage = buildDiscordReleaseMessage({
    version: "2.9.0",
    previousTag: "v2.9.0rc1",
    previousFinalTag: "v2.8.1",
    repository: "Pycord-Development/pycord",
  });
  assert.match(finalMessage, /@everyone/);
  assert.match(finalMessage, /compare\/v2\.8\.1\.\.\.v2\.9\.0/);
  const rcPayload = buildDiscordReleasePayload({
    version: "2.9.0rc1",
    previousTag: "v2.8.1",
    repository: "Pycord-Development/pycord",
  });
  assert.match(rcPayload.content, /@here/);
  assert.deepEqual(rcPayload.allowed_mentions, { parse: ["everyone", "roles"] });
});

test("Discord dry run does not require a webhook and live send validates the endpoint", async () => {
  const options = {
    version: "2.9.0",
    previousTag: "v2.8.1",
    repository: "Pycord-Development/pycord",
  };
  assert.equal((await sendDiscordReleaseNotification({ ...options, dryRun: true })).sent, false);
  await assert.rejects(
    sendDiscordReleaseNotification({ ...options, webhookUrl: "https://example.com/hook" }),
    /Discord webhook URL/,
  );
  let request;
  const sent = await sendDiscordReleaseNotification(
    { ...options, webhookUrl: "https://discord.com/api/webhooks/1/secret" },
    async (url, init) => {
      request = { url: String(url), init };
      return response(204);
    },
  );
  assert.equal(sent.sent, true);
  assert.equal(request.init.method, "POST");
  assert.equal(JSON.parse(request.init.body).allowed_mentions.parse[0], "everyone");
});

test("artifact digest helper agrees with Node crypto", () => {
  const artifacts = createArtifacts();
  const expected = `sha256:${createHash("sha256").update("wheel-content").digest("hex")}`;
  assert.equal(artifacts.wheelDigest, expected);
});
