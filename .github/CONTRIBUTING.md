## Contributing to Pycord

First off, thanks for taking the time to contribute. It makes the library substantially better. :+1:

The following is a set of guidelines for contributing to the repository. These are guidelines, not hard rules.

## This is too much to read! I want to ask a question!

Generally speaking questions are better suited in our resources below.

- The official support server: https://pycord.dev/discord
- [The FAQ in the documentation](https://docs.pycord.dev/en/master/faq.html)
- [StackOverflow's `pycord` tag](https://stackoverflow.com/questions/tagged/pycord)

Please try your best not to ask questions in our issue tracker. Most of them don't belong there unless they provide value to a larger audience.

## Good Bug Reports

Please be aware of the following things when filing bug reports.

1. Don't open duplicate issues. Please search your issue to see if it has been asked already. Duplicate issues will be closed.
2. When filing a bug about exceptions or tracebacks, please include the *complete* traceback. Without the complete traceback the issue might be **unsolvable** and you will be asked to provide more information.
3. Make sure to provide enough information to make the issue workable. The issue template will generally walk you through the process but they are enumerated here as well:
    - A **summary** of your bug report. This is generally a quick sentence or two to describe the issue in human terms.
    - Guidance on **how to reproduce the issue**. Ideally, this should have a small code sample that allows us to run and see the issue for ourselves to debug. **Please make sure that the token is not displayed**. If you cannot provide a code snippet, then let us know what the steps were, how often it happens, etc.
    - Tell us **what you expected to happen**. That way we can meet that expectation.
    - Tell us **what actually happens**. What ends up happening in reality? It's not helpful to say "it fails" or "it doesn't work". Say *how* it failed, do you get an exception? Does it hang? How are the expectations different from reality?
    - Tell us **information about your environment**. What version of Pycord are you using? How was it installed? What operating system are you running on? These are valuable questions and information that we use.

If the bug report is missing this information then it'll take us longer to fix the issue. We will probably ask for clarification, and barring that if no response was given then the issue will be closed.

## Submitting a Pull Request

Submitting a pull request is fairly simple, just make sure it focuses on a single aspect and doesn't manage to have scope creep and it's probably good to go. It would be incredibly lovely if the style is consistent to that found in the project. This project follows PEP-8 guidelines (mostly) with a column limit of 125.

## Use of "type: ignore" comments
In some cases, it might be necessary to ignore type checker warnings for one reason or another.
If that is that case, it is **required** that a comment is left explaining why you are
deciding to ignore type checking warnings.

### Licensing

By submitting a pull request, you agree that; 1) You hold the copyright on all submitted code inside said pull request; 2) You agree to transfer all rights to the owner of this repository, and; 3) If you are found to be in fault with any of the above, we shall not be held responsible in any way after the pull request has been merged.

## Git Commit Styling

Not following this guideline could lead to your pull being squashed for a cleaner commit history

Some style guides we would recommed using in your pulls:

The [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) style is a very widely used style and a good style to start with.

The [gitmoji](https://gitmoji.dev) style guide would make your pull look more lively and different to others.

We don't limit nor deny your pulls when you're using another style although, please make sure it is appropriate and makes sense in this library.
