-- scheduler.lua — entry point for the Pure Lua Scheduler plugin.
--
-- This plugin is intentionally Lua-only (no plugin.py) to exercise the
-- CodeQL workflow's "skipped + unscanned: lua" detection path.
-- Expected workflow result:
--   - detect-langs: found=false, unscanned_langs=lua
--   - CodeQL: skipped
--   - PR comment: "CodeQL analysis was skipped - ... lua"

local function now_iso()
  return os.date("!%Y-%m-%dT%H:%M:%SZ")
end

local function schedule(tasks)
  local results = {}
  for _, task in ipairs(tasks) do
    local entry = {
      name      = task.name or "unnamed",
      scheduled = task.cron or "* * * * *",
      last_run  = now_iso(),
      status    = "pending",
    }
    results[#results + 1] = entry
    io.write(string.format("[%s] scheduled: %s (%s)\n", entry.last_run, entry.name, entry.scheduled))
  end
  return results
end

-- Default demo schedule when run standalone.
local demo_tasks = {
  { name = "prune-old-streams", cron = "0 3 * * *" },
  { name = "refresh-epg",       cron = "0 */6 * * *" },
  { name = "health-report",     cron = "*/15 * * * *" },
}

schedule(demo_tasks)
