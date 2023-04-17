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
