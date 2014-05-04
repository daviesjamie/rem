Todor
=====

> Todor? Todor, todor.

Todor is a simple Python tool that enables you to create plain-text todo lists
on a per-project basis. Think of it as Git for your todos.

![Example
workflow](https://github.com/daviesjamie/todor/raw/master/workflow.png)

## Installation

To install Todor, simply clone the repository and then add an alias to the
`todor.py` executable:

```
$ git clone https://github.com/daviesjamie/todor ~/Code/todor
$ alias todor='~/Code/todor.py'
```

## Usage

To use Todor, you first have to create a task list in your project directory
with the `init` command. Once this has been performed, then using any other
`todor` commands within the project directory (including any subdirectories)
will act upon that task list. However, if you are in a directory that is not
within the project's directory tree, then Todor will not access the project's
task list.

This enables you to create and act upon separate task lists for each project you
work on, and as they are simply plain text files they can even be version
controlled along with the contents of your project!

The following commands can be given to Todor:
 - `init`<br />
   Initialises a task list in the current directory.

 - `add [-f|--file] <task>`<br />
   Adds a task to the list.<br />
   If the `-f` flag is specified, the system `$EDITOR` is opened instead, and
   each line in the document when the editor is closed will be added as a task.

 - `edit <prefix> <text>`<br />
   Replaces the a task's contents with the supplied text.<br />
   The text argument can also be a substitution in the form
   `/match/replacement/` to apply a find and replace on the existing task text.

 - `done <prefix>`<br />
   Marks a task as completed. Multiple task prefixes can be supplied
   to mark them all as complete.

 - `rm <prefix>`<br />
   Deletes a task. Multiple task prefixes can be supplied to delete them all.

 - `ls [-d|--done] [-s|--short||-l|--long] [-g|--grep]`<br />
   Lists the tasks that have yet to be completed. All tasks are prefixed by
   unique identifiers, which are used to select tasks for use with other
   commands.

   The `--done` flag can be given to instead list completed tasks.

   `--short` can be used to only display the task text (and not their prefixes),
   and `--long` can be used to display the full task identifiers and not just
   the number of characters needed to make unique identifiers.

   `--grep` can be used to filter the task list to include only those with the
   given search term(s).


## Credits

To create Todor, small amounts of code and inspiration were taken from Steve
Losh's [t](http://stevelosh.com/projects/t/) project, and the
[Mercurial](http://mercurial.selenic.com/) code base.
