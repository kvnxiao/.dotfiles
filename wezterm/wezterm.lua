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
    set_environment_variables = {
      MSYS2_ARG_CONV_EXCL = "*",
      MSYS = "winsymlinks:nativestrict",
      CHERE_INVOKING = "1",
      MSYSTEM = "MINGW64",
      MSYS2_PATH_TYPE = "inherit",
      SHELL = "/usr/bin/zsh",
    },
    default_prog = {
      -- "C:\\Program Files\\PowerShell\\7\\pwsh.exe", "-nologo"
      "C:\\msys64\\usr\\bin\\env.exe",
      "MSYS2_ARG_CONV_EXCL=*",
      "MSYS=enable_pcon winsymlinks:nativestrict",
      "MSYS2_PATH_TYPE=inherit",
      "MSYSTEM=MSYS",
      "/usr/bin/zsh", "--login",
    },
    font = wezterm.font_with_fallback({
      "FiraCode NF",
      "FiraCode Nerd Font",
      "JetBrains Mono",
    }),
    font_size = 13,
    window_decorations = "RESIZE",
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
        key = "t",
        mods = "CTRL",
        action = wezterm.action.SpawnTab "CurrentPaneDomain"
      },
      {
        key = "w",
        mods = "CTRL",
        action = wezterm.action.CloseCurrentTab { confirm = false },
      }
    }
  }
end

local function get_unix_config()
  return {
    default_prog = { "/bin/zsh", "-l" },
    set_environment_variables = {},
    font = wezterm.font_with_fallback({
      "FiraCode Nerd Font",
      "JetBrains Mono",
    }),
    font_size = 16,
    window_decorations = "RESIZE",
    keys = {}
  }
end

local platform_config
if wezterm.target_triple == "x86_64-pc-windows-msvc" then
  platform_config = get_windows_config()
else
  platform_config = get_unix_config()
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
    -- Ctrl-click will open the link under the mouse cursor
    {
      event = { Up = { streak = 1, button = "Left" } },
      mods = "CTRL",
      action = "OpenLinkAtMouseCursor",
    },
    -- Disable the 'Down' event of CTRL-Click to avoid weird program behaviors
    {
      event = { Down = { streak = 1, button = "Left" } },
      mods = "CTRL",
      action = "Nop",
    },
  },

  keys = platform_config.keys
}
