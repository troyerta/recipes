## Write me

Like any software framework, RBook relies on a few assumptions and rules about it's use in order for the tool to work correctly. Here are a few tips to follow for a successful use of the framework:

1. RBook uses a third-party website generator, called 'mdbook'. This tool is free and open source, and the RBook tool has control over the generated website styles, layouts, and features as provided by mdbook. In other words, RBook is completely at the mercy of mdbook. Any limitation that mdbook has, RBook also has. If you desire a different static website backend, RBook may have limited usefulness for you.

2. RBook recipe files follow a recommended style. This is not to crush the creative spirit of the author, but to provide strong guarantees around the portability and consistency of your recipes. RBook has a number of features that can be thought of as fancy "spellcheckers". Every time you run the Rbook processor, these features expect a degree of consistency in recipe formatting and content to work well. There are of course, ways to set of use a preferred sytle in your recipes, and these are outlined in the tutorial. But, the closer your recipes stick to the recommended style, the easier it will be to:

- Keep every recipe page looking "pretty", well spaced, organized, searchable, and consistent.

- Perform mass re-formatting and restyling operations, which can change the look of every recipe in the entire book all at once.

3.
