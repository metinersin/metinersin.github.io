# frozen_string_literal: true

require "kramdown/parser/kramdown"

# Kramdown normally reserves $$...$$ for both inline and display math. Teach its
# inline parser the conventional $...$ form so Markdown does not alter TeX before
# MathJax receives it. The existing block parser continues to handle $$...$$.
inline_math = Kramdown::Parser::Kramdown.parser(:inline_math)
inline_math.start_re = /(?<!\\)(?<!\$)\$(?![\$\s])(.+?)(?<![\\\s])\$(?!\$)/m

# Preserve the backslash in \$ so MathJax's processEscapes option can distinguish
# literal currency signs from math delimiters after Markdown conversion.
module SingleDollarMathEscapes
  def parse_escaped_chars
    @src.pos += @src.matched_size
    add_text(@src[1] == "$" ? "\\$" : @src[1])
  end
end

Kramdown::Parser::Kramdown.prepend(SingleDollarMathEscapes)
