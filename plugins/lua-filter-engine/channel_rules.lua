-- channel_rules.lua
-- Bundled filter/ranking script for the Lua Filter Engine plugin.
-- Reads a JSON payload from stdin (channels list + min_score),
-- applies scoring rules, and writes the filtered list to stdout.
--
-- This file is intentionally written in Lua to exercise the CodeQL workflow's
-- "unscanned language" detection (Lua is not supported by CodeQL).

local json = require("cjson")   -- luarocks install lua-cjson

local raw = io.read("*a")
local data = json.decode(raw)

local channels = data.channels or {}
local min_score = tonumber(data.min_score) or 0

local function score(ch)
  local s = 50
  -- Prefer channels with a low channel number (feels more "real").
  if ch.number and ch.number < 100 then s = s + 20 end
  if ch.number and ch.number < 50  then s = s + 10 end
  -- Boost channels whose name contains an HD/UHD indicator.
  local name = (ch.name or ""):lower()
  if name:find("uhd") or name:find("4k") then s = s + 15 end
  if name:find("%shd") or name:find("hd%s") or name:match("hd$") then s = s + 5 end
  return s
end

local result = {}
for _, ch in ipairs(channels) do
  local s = score(ch)
  if s >= min_score then
    ch.score = s
    result[#result + 1] = ch
  end
end

-- Sort descending by score.
table.sort(result, function(a, b) return a.score > b.score end)

io.write(json.encode(result))
io.write("\n")
