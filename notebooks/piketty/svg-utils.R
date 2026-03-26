library(rsvg)

build_svg <- function(svg_content, replace_list = NULL){
  if (!is.character(svg_content) || length(svg_content) != 1) {
    stop("svg_content must be a single string.")
  }

  if (!is.null(replace_list)) {
    if (!is.list(replace_list)) {
      stop("replace_list must be a named list of string-to-string replacements.")
    }

    replacement_keys <- names(replace_list)
    if (is.null(replacement_keys) || any(replacement_keys == "")) {
      stop("replace_list must be a named list where each name is the string to replace.")
    }

    for (i in seq_along(replace_list)) {
      svg_content <- gsub(replacement_keys[i], replace_list[[i]], svg_content, fixed = TRUE)
    }
  }

  f <- tempfile(fileext = ".svg")
  writeLines(svg_content, f)
  f
}
