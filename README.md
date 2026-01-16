# static-site-generator
A program made to generate HTML from markdown, producing static web pages.

This program was created based on the guided project of the same name on [boot.dev](https://boot.dev/).
The difference between them is the presence of a pretty printing feature that I included in the work!
That is, the HTML files generated from markdown will be pretty-printed.

## Usage

Place markdown files under `./content`, entitled `index.md`, letting each correspond to either the directory,
or any one subdirectory.

Place a `styles.css` file under the `./static` directory, and any images you reference within the markdown files
within its `/images` subdirectory.

Run `main.sh`, and your static web pages will be generated recursively!
