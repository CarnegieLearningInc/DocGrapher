# DocGrapher
Utility to graph connections between text documents, using a lightweight annotation scheme.

[Todo: screenshot]

## Purpose
When managing large projects with many contributors that can span multiple years of development and research, a code base can grow unwieldy. This project is designed to help developers and researchers understand the relationships between files. 

This project has two main goals:

1. When making code changes, it should be quick and easy to understand the effects of those changes.
2. When beginning work on a project (or after a long break), it should be easy to understand how files share code and functionality to quickly facilitate modifications.

To accomplish these goals, we define a simple annotation scheme that authors insert into their text documents. The annotation scheme defines simple relationships between files, which can then be graphically and interactively displayed in the web browser.

## Use Cases

This section describes the uses cases for which this project was defined.

#### Research Project

Research code often has several non-desirable features:
* Many small utilities are each focused on a specific, narrow task (e.g., data cleanup, analysis)
* Many variations of the same task, each specialized for different data sets, are separated out into individual files.

Suppose a researcher, Steve, comes to a project that Bob and Rob have been working on. Bob wrote the initial code, called `best_analysis_ever`. Later on, Rob found the `best_analysis_ever` and, agreeing that this analysis was great, tried to apply it to his new dataset. Unfortunately, Rob found a few errors in Bob's code. He fixed them for this new analysis, though he didn't bubble the changes up to the initial file for fear of breaking things in the original analysis (and Rob was on a tight deadline).

When Steve starts his work on the project, he sees two files that may be relevant to his needs: Bob's `best_analysis_ever` and Rob's `superduper_analysis`. How will he know to choose the `superduper_analysis`, with all of its modifications?

Our system allows for simple annotations to convey that `best_analysis_ever` was the original file, and that `superduper_analysis` came later, with improvements.

#### Software Development Project

Software development tends to be a little bit more straightforward, with simpler hierarchies and well-defined objects interacting with other objects in well-defined ways. Still, if the project has source code across multiple languages it may be difficult to get a bird's eye view of the project. Our annotation scheme can help.

Suppose software-developer Susan has been assigned to make a small modification to a component of an app called `Mr Mustacher`, which allows users to upload pictures of their friends with funny captions and the software adds a mustache to the face. It's rad.

Susan needs to fix a unicode bug in the uploading process where the text caption is not correctly transferred from the website to the server (unfortunately, non-ascii characters are being omitted). Coming into this project, it is not immediately obvious where the communication between the website and server take place.

A graph of this project generated with DocGrapher will show two distinct subgraphs -- one containing files for the website (that handle user input) and another with files from the server (that adds a mustache and caption). The communication between those two components will be represented as a single edge between two large subgraphs, clearly marking Susan's points of investigation.

## Annotation Scheme

The DocGrapher will crawl through every file in a specified directory looking for annotations. When found, the files and their corresponding annotations are added to the graph. The annotations are:

* `@name`: A unique name given to this file. 
  * This name **must** be unique to a graph, because it will be referenced by other nodes.
  * We use a user-defined name instead of the filename for readability in the graph and to be robust to filename changes.
* `@note`: A brief note about the file -- what it does, changes made since the last iteration, etc.
* `@imports`: Any files that the current file imports. 
  * This is a very important connection, since any changes to the imported file may impact the current file.
  * In the future, there will be an "AUTO" option that automagically infers the imports.
  * This does **not** include shared code from copy-pasting (see `@forks` below).
  * This is a comma-separated list of `@names`.
* `@forks`: Any files that the current file takes functionality from.
  * For example, if there is a file named `analysis` and we create a new file to specialize the analysis to a specific dataset (`analysis_data1`), then `analysis_data1` will "`@fork`" `analysis`.
  * This is a comma-separated list of `@names`.
* `@uses`: Any files that the current file uses as input in order to run.
  * Typically, this is used to demystify the types of files a program (e.g., a server) takes as input.
  * For example, the `doc_grapher.html` file in this repository "`@uses`" the `create_docgraph.py` script to display its data.
    * Note that `doc_grapher` does not literally take `create_docgraph` as input, but rather the `doc_grapher` input is the output from `create_docgraph`.
  * This is a comma-separated list of `@names`.

#### Notes 

* `FileA` can both `@import` and `@fork` the same `FileB` if:
  * `FileA` imports `FileB` code directly from `FileB` (e.g., **not** copy-pasted); and
  * `FileA` shares significant functionality with `FileB`, perhaps addressing a specific dataset as described above.
* It is less common for a file to `@import` and `@use` the same file, though it is not prohibited.
* A file **cannot** both `@fork` and `@use` a single file; these are mutually exclusive.
  * The `create_docgraph` python script will throw an error if it finds this

## How To Use the Utility
Todo..

## Examples
Todo..
