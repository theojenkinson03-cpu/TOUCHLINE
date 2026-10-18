"""6 Again branding inside the script."""

def apply(js, rep, resub, replace_function):
    js = rep(js, "'touchline-updated'", "'sixagain-updated'")
    js = rep(js, "A new version of Touchline has downloaded.", "A new version of 6 Again has downloaded.")
    js = rep(js, "the text is not a Touchline backup", "the text is not a 6 Again backup")
    js = rep(js, "`Touchline_backup_${", "`6Again_backup_${")
    js = rep(js, "'Touchline_unreadable_save.json'", "'6Again_unreadable_save.json'")
    js = rep(js, "'touchline-tips'", "'sixagain-tips'", 2)
    js = rep(js, "Error('Not a Touchline save')", "Error('Not a 6 Again save')")
    js = rep(js, "newer version of Touchline", "newer version of 6 Again")
    js = rep(js, "app:'touchline'", "app:'sixagain'")
    js = resub(js, r"(?i)#d6f498", "#ffd166", None, 'lime')
    return js
