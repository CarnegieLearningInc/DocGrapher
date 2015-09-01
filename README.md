# DocGrapher
Utility to graph connections between text documents, using a lightweight annotation scheme.

[Todo: screenshot]

## Purpose
When managing large projects with many contributors that can span multiple years of development and research, a code base can grow unwieldy. This project is designed to help developers and researchers understand the relationships between files, which is important for two main reasons:

1. When making changes, it should be quick and easy to understand the effects of those changes.
2. When beginning work on a project (or after a long break), it should be easy to understand how files share code and functionality to quickly facilitate modifications.

This utility works towards these goals by defining a simple annotation scheme that authors insert into their files. The annotation scheme defines simple relationships between files, which can then be graphically and interactively displayed in the web browser.

## Use Cases

This section describes the uses cases for which this project was defined.

#### Research Project

Research code often has several non-desirable features:
* Many small utilities that are focused on a specific, narrow task (e.g., data cleanup, analysis)
* Many variations of the same task, specialized for different data sets.

Suppose a researcher, Steve, comes to a project that Bob and Rob have been working on. Bob wrote the initial code, called `best_analysis_ever`. Later on, Rob found the `best_analysis_ever` and, agreeing that this analysis was great, tried to apply it to his new dataset. Unfortunately, Rob found a few errors in Bob's code and fixed them for this new analysis, though he didn't bubble the changes up to the initial file for fear of breaking things in the original analysis.

When Steve comes to the project, he sees two files that ma be relevant to his needs: Bob's `best_analysis_ever` and Rob's `superduper_analysis`. How will he know to choose the `superduper_analysis`, with all of its modifications?

Our system allows for simple annotations to convey that `best_analysis_ever` was the original file, and that `superduper_analysis` came later, with improvements.

#### Software Development Project

Software development tends to be a little bit more straightforward, with simpler hierarchies and well-defined objects interacting with other objects in well-defined ways. Still, if the project has source code across multiple languages it may be difficult to get a bird's eye view of the project. In particular, it may not be obvious where the main functions and executables live. Our annotation scheme can help.

Suppose software-developer Susan has been assigned to make a small modification to a component of a large app called `The Mustacher`. `Mr Mustacher` allows users to upload images with funny captions and the software adds a mustache to the face. It's rad.

Susan needs to fix a unicode bug in the uploading process where the text caption is not correctly transferred from the website to the server (unfortunately, non-ascii characters are being omitted). Coming into this project, it is not immediately obvious where the communication between the website and 

A graph of this project generated with DocGrapher will show two distinct subgraphs -- one that handles user input and the other that processes that input and adds a mustache. The communication between those two components will be represented as a single edge between two large subgraphs, clearly marking the points of investigation to Susan.

## Annotation Schema

The DocGrapher will crawl through every file in a specified directory looking for annotations. When found, the files and their corresponding annotations are added to the graph. The annotations are:

* `@name`: A unique name given to this file. 
  * This name **must** be unique to a graph, because it will be referenced by other nodes.
  * We use a user-defined name instead of the filename for readability in the graph and to be robust to filename changes.
* `@note`: A brief note about the file -- what it does, changes made since the last iteration, etc.
* `@imports`: Any files that this file imports. This is a very important connection, since any changes to the imported file may impact the current file.
  * In the future, there will be an "AUTO" option that automagically infers the imports.
  * This does **not** include shared code from copy-pasting (see `@forks` below).
  * This is a comma-separated list of `@name`s.
* `@forks`: Any files that the current file takes functionality from.
  * For example, if there is a file named `analysis` and we create a new file to specialize the analysis to a specific dataset (`analysis_data1`), then `analysis_data1` will "`@fork`" `analysis`.
  * This is a comma-separated list of `@name`s.
* `@uses`: Any files that the current file uses as input in order to function.
  * Typically, this is used to demystify the types of files a server takes as input.
  * For example, the `doc_grapher.html` file "`@uses`" the `create_docgraph.py` script to display its data.
    * Note that `doc_grapher` does not literally take `create_docgraph` as input, but rather the `doc_grapher` input is `create_docgraph`'s output.

#### Notes 

* `FileA` can both `@import` and `@fork` the same `FileB` if:
  * `FileA` imports `FileB` code directly from `FileB` (e.g., NOT copy-pasted); and
  * `FileA` shares significant functionality with `FileB`, perhaps addressing a specific dataset as described above.
* It is less common for a file to `@import` and `@use` the same file, though it is not prohibited.
* A file **cannot** both `@fork` and `@use` a single file; these are mutually exclusive.
  * The `create_docgraph` python script will throw an error if it finds this



## Examples
Todo..
