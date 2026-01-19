document.addEventListener("DOMContentLoaded", () => {
  const tables = document.querySelectorAll(".py-attribute-table[data-move-to-id]");
  tables.forEach((table) => {
    let element = document.getElementById(table.getAttribute("data-move-to-id"));
    let parent = element.parentNode;
    // insert ourselves after the element
    parent.insertBefore(table, element.nextSibling);
  });

  // This can be replaced once the css :has() selector is mainstream
  // https://developer.mozilla.org/en-US/docs/Web/CSS/:has
  // .reference.internal:has(code) + ul
  const tocObjects = document.querySelectorAll(
    ".toc-tree li > .reference.internal:not(:only-child) code",
  );
  tocObjects.forEach((e) => {
    e.parentElement.parentElement
      .querySelector(".reference.internal + ul")
      .classList.add("has-selector-alternative");
  });
});

// We could use this css instead, but it doesn't allow for the transition
// :not(.scroll-current) > .reference.internal:has(code) + ul:not(:has(.scroll-current))

const getCurrentTocObject = (e) => {
  let target = null;
  let next = e.target;
  while (true) {
    if (
      next.firstElementChild.classList.contains("reference") &&
      next.firstElementChild.firstElementChild?.localName === "code"
    ) {
      target = next;
      next = target.parentElement.parentElement;
    } else {
      break;
    }
  }
  return target?.querySelector("ul");
};

document.addEventListener("gumshoeActivate", (e) => {
  const target = getCurrentTocObject(e);
  if (target) {
    target.style.maxHeight = target.scrollHeight + "px";
  }
});

document.addEventListener("gumshoeDeactivate", (e) => {
  const target = getCurrentTocObject(e);
  if (target) {
    target.style.maxHeight = "0px";
  }
});

// Content Width Toggle Functionality
const CONTENT_WIDTH_KEY = "pycord-docs-content-width";

(() => {
  const savedWidth = localStorage.getItem(CONTENT_WIDTH_KEY);
  const isWide = savedWidth === "wide";
  if (isWide) {
    document.body.classList.add("wide-mode");
  }
})();

document.addEventListener("DOMContentLoaded", () => {
  const standardRadio = document.getElementById("standard-width-radio");
  const wideRadio = document.getElementById("wide-width-radio");

  if (!standardRadio || !wideRadio) return;

  const savedWidth = localStorage.getItem(CONTENT_WIDTH_KEY);
  const isWide = savedWidth === "wide";

  if (isWide) {
    wideRadio.checked = true;
  } else {
    standardRadio.checked = true;
  }

  standardRadio.addEventListener("change", () => {
    if (standardRadio.checked) {
      localStorage.setItem(CONTENT_WIDTH_KEY, "standard");
      document.body.classList.remove("wide-mode");
    }
  });

  wideRadio.addEventListener("change", () => {
    if (wideRadio.checked) {
      localStorage.setItem(CONTENT_WIDTH_KEY, "wide");
      document.body.classList.add("wide-mode");
    }
  });
});
