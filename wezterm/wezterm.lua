local wezterm = require "wezterm";

local function scheme_for_appearance(appearance)
  if appearance:find "Dark" then
    return "Catppuccin Mocha"
  else
    return "Catppuccin Latte"
  end
end

local function get_windows_config()
  return {
    audible_bell = "Disabled",
    set_environment_variables = {
      MSYS = "enable_pcon winsymlinks:nativestrict",
      CHERE_INVOKING = "1",
      MSYSTEM = "MSYS",
      MSYS2_PATH_TYPE = "inherit",
      SHELL = "/usr/bin/fish",
    },
    default_prog = {
      "C:\\msys64\\usr\\bin\\fish.exe",
      "-i"
    },
    font = wezterm.font_with_fallback({
      { family = "FiraCode Nerd Font Mono", weight = "Regular", stretch = "Normal", style = "Normal" },
      "JetBrains Mono",
    }),
    font_size = 13,
    window_decorations = "RESIZE",
    max_fps = 120,
    keys = {
      {
        key = "c",
        mods = "CTRL",
        action = wezterm.action_callback(function(win, pane)
          local has_selection = win:get_selection_text_for_pane(pane) ~= ""
          if has_selection then
            win:perform_action(wezterm.action { CopyTo = "ClipboardAndPrimarySelection" }, pane)
            win:perform_action("ClearSelection", pane)
          else
            win:perform_action(wezterm.action { SendKey = { key = "c", mods = "CTRL" } }, pane)
          end
        end)
      },
      {
        key = "v",
        mods = "CTRL",
        action = wezterm.action { PasteFrom = "Clipboard" }
      },
      {
        key = "t",
        mods = "CTRL",
        action = wezterm.action.SpawnTab "CurrentPaneDomain"
      },
      {
        key = "w",
        mods = "CTRL",
        action = wezterm.action.CloseCurrentTab { confirm = false },
      },
      {
        key = "Backspace",
        mods = "CTRL",
        action = wezterm.action { SendString = "\x17" },
      }
    }
  }
end

local function get_macos_config()
  return {
    default_prog = { "/opt/homebrew/bin/fish", "-l" },
    set_environment_variables = {},
    font = wezterm.font_with_fallback({
      "FiraCode Nerd Font",
      "JetBrains Mono",
    }),
    max_fps = 120,
    font_size = 16,
    window_decorations = "RESIZE",
    keys = {
      -- Ctrl+Shift+Arrow → word selection (override WezTerm default ActivatePaneDirection)
      { key = "LeftArrow", mods = "CTRL|SHIFT", action = wezterm.action { SendString = "\x1b[1;6D" } },
      { key = "RightArrow", mods = "CTRL|SHIFT", action = wezterm.action { SendString = "\x1b[1;6C" } },
      -- Opt+Shift+Arrow → word selection (Karabiner remaps Cmd+Shift+Arrow to this)
      { key = "LeftArrow", mods = "ALT|SHIFT", action = wezterm.action { SendString = "\x1b[1;6D" } },
      { key = "RightArrow", mods = "ALT|SHIFT", action = wezterm.action { SendString = "\x1b[1;6C" } },
      -- Cmd+Backspace → word delete
      { key = "Backspace", mods = "SUPER", action = wezterm.action { SendString = "\x17" } },
    }
  }
end

local function get_linux_config()
  return {
    default_prog = { "/bin/zsh", "-l" },
    set_environment_variables = {},
    font = wezterm.font_with_fallback({
      "FiraCode Nerd Font",
      "JetBrains Mono",
    }),
    max_fps = 120,
    font_size = 16,
    window_decorations = "RESIZE",
    keys = {}
  }
end

local is_macos = wezterm.target_triple == "aarch64-apple-darwin"
  or wezterm.target_triple == "x86_64-apple-darwin"

local platform_config
if wezterm.target_triple == "x86_64-pc-windows-msvc" then
  platform_config = get_windows_config()
elseif is_macos then
  platform_config = get_macos_config()
else
  platform_config = get_linux_config()
end

local link_mod = is_macos and "SUPER" or "CTRL"

-- Global keybindings (merged with platform-specific keys)
local global_keys = {
  {
    key = "Enter",
    mods = "SHIFT",
    action = wezterm.action { SendString = "\x1b[13;2u" },
  },
}
for _, k in ipairs(global_keys) do
  table.insert(platform_config.keys, k)
end

return {
  default_prog = platform_config.default_prog,
  set_environment_variables = platform_config.set_environment_variables,
  initial_cols = 88,
  initial_rows = 24,
  default_cursor_style = "BlinkingBlock",
  animation_fps = 1,
  cursor_blink_ease_in = "Constant",
  cursor_blink_ease_out = "Constant",
  use_fancy_tab_bar = false,
  enable_scroll_bar = true,
  font = platform_config.font,
  font_size = platform_config.font_size,
  freetype_load_target = "Light",
  freetype_render_target = "HorizontalLcd",
  window_decorations = platform_config.window_decorations,
  window_close_confirmation = "NeverPrompt",
  color_scheme = scheme_for_appearance(wezterm.gui.get_appearance()),

  mouse_bindings = {
    -- Change the default selection behavior so that it only selects text,
    -- but doesn't copy it to a clipboard or open hyperlinks.
    {
      event = { Up = { streak = 1, button = "Left" } },
      mods = "NONE",
      action = wezterm.action { ExtendSelectionToMouseCursor = "Cell" }
    },
    {
      event = { Up = { streak = 1, button = "Left" } },
      mods = "SHIFT",
      action = "Nop",
    },
    -- Don't automatically copy the selection to the clipboard
    -- when double clicking a word
    {
      event = { Up = { streak = 2, button = "Left" } },
      mods = "NONE",
      action = "Nop",
    },
    -- Ctrl-click (Windows/Linux) or Cmd-click (macOS) to open links
    {
      event = { Up = { streak = 1, button = "Left" } },
      mods = link_mod,
      action = "OpenLinkAtMouseCursor",
    },
    -- Disable the 'Down' event to avoid weird program behaviors
    {
      event = { Down = { streak = 1, button = "Left" } },
      mods = link_mod,
      action = "Nop",
    },
  },

  keys = platform_config.keys
}
