local months = {
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
}

local function is_enabled(value)
  if type(value) == "boolean" then
    return value
  end

  return value ~= nil and pandoc.utils.stringify(value):lower() == "true"
end

local function git_date(source)
  local ok, output = pcall(
    pandoc.pipe,
    "git",
    {
      "-C",
      pandoc.path.directory(source),
      "log",
      "-1",
      "--format=%cs",
      "--",
      source,
    },
    ""
  )

  if not ok then
    return nil
  end

  return output:match("(%d%d%d%d%-%d%d%-%d%d)")
end

local function long_date(iso_date)
  local year, month, day = iso_date:match(
    "^(%d%d%d%d)%-(%d%d)%-(%d%d)$"
  )
  local month_name = months[tonumber(month)]

  if not year or not month_name then
    return nil
  end

  return string.format("%s %d, %s", month_name, tonumber(day), year)
end

function Pandoc(document)
  if not FORMAT:match("html")
      or not is_enabled(document.meta["show-last-updated"]) then
    return document
  end

  local source = quarto.doc.input_file
  local iso_date = source and git_date(source)
  local display_date = iso_date and long_date(iso_date)

  if not display_date then
    io.stderr:write(
      "Unable to determine the last Git update for "
        .. tostring(source)
        .. "; omitting the update date.\n"
    )
    return document
  end

  local update = pandoc.RawBlock(
    "html",
    '<p class="page-updated">Last updated <time datetime="'
      .. iso_date
      .. '">'
      .. display_date
      .. "</time></p>"
  )
  table.insert(document.blocks, 1, update)

  return document
end
