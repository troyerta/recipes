# RBook - Advanced Intro

## This introduction to RBook assumes you have some technical background with PCs

More specifically, if you are familiar with the following things:

- Common SW development tools like "git" and code editors

- Navigating your PC, using PATH variables, and running SW from the terminal or command line

Then this page is for you!

You will have an easier time using RBook to build and deploy your online cookbook, and once you see how it works, you'll know everything you need to customize RBook realize most of it's potential.

## What is RBook, really?

Simply put, RBook is a collection of existing SW tools that facilitate the creation and deployment of beautiful, useful, and minimal websites that serve as personal cookbooks. These websites are accessible from anywhere, easily to customize and maintain, and can be deployed by any hosting platform, including free domains such as github pages.

After a book is initially built, updating your book is typically as simple as copying, pasting, and saving new recipes before running a single Python script to fix up your book with new changes.

Aside from the Python scripts, RBook is mostly an MdBook project manager, built to support recipe-like pages, and automated updates where needed. MdBook is a rust application, and is best installed with cargo.

Aside from Python and MdBook, git is the remaining major software component. Git is mostly needed to track changes to the recipe book over time, and to provide a convenient method for deploying your book to githu-pages, where recipes books can be hosted for free.

Make - is an optional dependency, which automates the site deployment if your plan to use github-pages.

So RBook is really just like any other MdBook project, with a few Python scripts added to glue everything together.

## RBook Minimal Depenedencies

- Mdbook: For converting markdown to html
  - [github.com/rust-lang/mdBook/releases](https://github.com/rust-lang/mdBook/releases)

- Python 3.7.x+: For running the virtual python environment that manages your recipes in the book
  - [python.org/downloads/](https://www.python.org/downloads/)

- RBook project files: Contains a starter recipe book, tests, documentation, recipe samples, and RBook productivity scripts
  - [RBook repo](https://github.com/troyerta/recipes)

## Recommended Dependencies

- Hosting service: For serving up your recipe book website from anywhere
  - [pages.github.com/](https://pages.github.com/)

- Git: For tracking changes to the book and generated website, plus quick deployment to Github-Pages
  - [https://git-scm.com/../Installing-Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

- Text editor: For quick editing access to multiple source files
  - [Visual Studio Code](https://code.visualstudio.com/download)
