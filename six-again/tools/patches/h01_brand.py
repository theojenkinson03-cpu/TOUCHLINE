"""6 Again branding in the page shell."""

def apply(head, rep, resub):
    head = rep(head, "<title>Touchline — Rugby Manager</title>", "<title>6 Again — Rugby League Manager</title>")
    head = rep(head, 'apple-mobile-web-app-title" content="Touchline"', 'apple-mobile-web-app-title" content="6 Again"')
    head = rep(head, 'application-name" content="Touchline"', 'application-name" content="6 Again"')
    head = rep(head, '<button class="brand" data-act="menu"><i class="ball"></i>touchline<span style="color:#b9d28b">.</span></button>', '<button class="brand" data-act="menu" aria-label="6 Again home"><i class="ball"></i>6&nbsp;again<span style="color:#ffd166">.</span></button>')
    head = resub(head, r"#123b32", "#12213b", None, 'hdr')
    head = resub(head, r"#135a42", "#1d4e89", None, 'green')
    head = resub(head, r"(?i)#d6f498", "#ffd166", None, 'lime')
    head = resub(head, r"(?i)#b9d28b", "#ffd166", None, 'lime2')
    return head
