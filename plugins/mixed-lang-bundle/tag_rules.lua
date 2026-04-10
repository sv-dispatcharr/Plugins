-- tag_rules.lua — custom channel tagging rules for the Mixed Lang Bundle plugin.
-- Called from plugin.py (via subprocess) with a JSON channel list on stdin.
-- Returns the same list with a "tags" array added to each entry.
--
-- Bundled as Lua to exercise the "unscanned language: lua" detection path
-- in the CodeQL workflow.

local ok, json = pcall(require, "cjson")
if not ok then
  -- Fallback: try dkjson (pure-Lua JSON library).
  json = require("dkjson")
end

local raw = io.read("*a")
local data, _, err = json.decode and json.decode(raw) or json.decode(raw, 1, nil)
if not data then
  io.stderr:write("tag_rules.lua: JSON parse error: " .. tostring(err) .. "\n")
  os.exit(1)
end

local function make_tags(ch)
  local name = (ch.name or ""):lower()
  local tags = {}
  if name:find("news") then tags[#tags+1] = "news" end
  if name:find("sport") or name:find("espn") or name:find("fox sport") then tags[#tags+1] = "sports" end
  if name:find("movie") or name:find("cinema") or name:find("film") then tags[#tags+1] = "movies" end
  if name:find("kid") or name:find("child") or name:find("cartoon") then tags[#tags+1] = "kids" end
  if name:find("music") or name:find("mtv") then tags[#tags+1] = "music" end
  if #tags == 0 then tags[#tags+1] = "general" end
  return tags
end

for _, ch in ipairs(data) do
  ch.tags = make_tags(ch)
end

io.write(json.encode(data))
io.write("\n")
