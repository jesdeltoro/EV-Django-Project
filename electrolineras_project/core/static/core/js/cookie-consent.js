(function () {
  "use strict";

  var COOKIE_NAME = "evemaps_cookie_consent";
  var CONSENT_VERSION = 1;
  var COOKIE_MAX_AGE = 60 * 60 * 24 * 180;
  var CATEGORIES = ["preferences", "analytics", "marketing"];
  var OPTIONAL_COOKIE_PATTERNS = {
    preferences: [],
    analytics: [/^_ga(?:_|$)/, /^_gid$/, /^_gat(?:_|$)/],
    marketing: [/^_fbp$/, /^fr$/]
  };

  var banner = document.getElementById("cookie-banner");
  var dialog = document.getElementById("cookie-dialog");
  var dialogPanel = dialog ? dialog.querySelector("[role='dialog']") : null;
  var lastFocusedElement = null;

  if (!banner || !dialog || !dialogPanel) {
    return;
  }

  function defaultConsent() {
    return {
      version: CONSENT_VERSION,
      necessary: true,
      preferences: false,
      analytics: false,
      marketing: false
    };
  }

  function readCookie(name) {
    var prefix = name + "=";
    var cookies = document.cookie ? document.cookie.split(";") : [];

    for (var index = 0; index < cookies.length; index += 1) {
      var cookie = cookies[index].trim();
      if (cookie.indexOf(prefix) === 0) {
        return cookie.substring(prefix.length);
      }
    }

    return null;
  }

  function readConsent() {
    var storedValue = readCookie(COOKIE_NAME);
    if (!storedValue) {
      return null;
    }

    try {
      var consent = JSON.parse(decodeURIComponent(storedValue));
      if (consent.version !== CONSENT_VERSION) {
        return null;
      }

      var normalizedConsent = defaultConsent();
      CATEGORIES.forEach(function (category) {
        normalizedConsent[category] = consent[category] === true;
      });
      return normalizedConsent;
    } catch (error) {
      return null;
    }
  }

  function writeConsent(consent) {
    var value = encodeURIComponent(JSON.stringify(consent));
    var secure = window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie = COOKIE_NAME + "=" + value + "; Max-Age=" + COOKIE_MAX_AGE + "; Path=/; SameSite=Lax" + secure;
  }

  function expireCookie(name) {
    var hostname = window.location.hostname;
    var domains = ["", hostname, "." + hostname];
    domains.forEach(function (domain) {
      var domainAttribute = domain ? "; Domain=" + domain : "";
      document.cookie = name + "=; Max-Age=0; Path=/; SameSite=Lax" + domainAttribute;
    });
  }

  function clearCategoryCookies(category) {
    var patterns = OPTIONAL_COOKIE_PATTERNS[category] || [];
    document.cookie.split(";").forEach(function (cookie) {
      var name = cookie.split("=")[0].trim();
      if (patterns.some(function (pattern) { return pattern.test(name); })) {
        expireCookie(name);
      }
    });
  }

  function activateResources(category) {
    var links = document.querySelectorAll("link[data-cookie-category='" + category + "'][data-cookie-href]");
    links.forEach(function (link) {
      if (!link.getAttribute("href")) {
        link.setAttribute("href", link.getAttribute("data-cookie-href"));
      }
    });

    var scripts = document.querySelectorAll("script[type='text/plain'][data-cookie-category='" + category + "']:not([data-cookie-loaded])");
    scripts.forEach(function (blockedScript) {
      var activeScript = document.createElement("script");
      Array.prototype.slice.call(blockedScript.attributes).forEach(function (attribute) {
        if (["type", "data-cookie-category", "data-cookie-src"].indexOf(attribute.name) === -1) {
          activeScript.setAttribute(attribute.name, attribute.value);
        }
      });

      var source = blockedScript.getAttribute("data-cookie-src");
      if (source) {
        activeScript.src = source;
      } else {
        activeScript.text = blockedScript.textContent;
      }

      blockedScript.setAttribute("data-cookie-loaded", "true");
      blockedScript.parentNode.insertBefore(activeScript, blockedScript.nextSibling);
    });
  }

  function applyConsent(consent) {
    CATEGORIES.forEach(function (category) {
      if (consent[category]) {
        activateResources(category);
      } else {
        clearCategoryCookies(category);
      }
    });

    document.documentElement.setAttribute("data-cookie-consent", "configured");
    window.dispatchEvent(new CustomEvent("evemaps:cookie-consent", { detail: consent }));
  }

  function syncInputs(consent) {
    CATEGORIES.forEach(function (category) {
      var input = dialog.querySelector("[data-cookie-category-input='" + category + "']");
      if (input) {
        input.checked = consent[category] === true;
      }
    });
  }

  function getSelectedConsent() {
    var consent = defaultConsent();
    CATEGORIES.forEach(function (category) {
      var input = dialog.querySelector("[data-cookie-category-input='" + category + "']");
      consent[category] = Boolean(input && input.checked);
    });
    return consent;
  }

  function persistConsent(consent) {
    writeConsent(consent);
    applyConsent(consent);
    banner.hidden = true;
    closeDialog();
  }

  function acceptAll() {
    var consent = defaultConsent();
    CATEGORIES.forEach(function (category) {
      consent[category] = true;
    });
    persistConsent(consent);
  }

  function rejectOptional() {
    persistConsent(defaultConsent());
  }

  function openDialog(trigger) {
    lastFocusedElement = trigger || document.activeElement;
    syncInputs(readConsent() || defaultConsent());
    dialog.hidden = false;
    document.body.classList.add("cookie-dialog-open");
    window.setTimeout(function () { dialogPanel.focus(); }, 0);
  }

  function closeDialog() {
    if (dialog.hidden) {
      return;
    }

    dialog.hidden = true;
    document.body.classList.remove("cookie-dialog-open");
    if (lastFocusedElement && typeof lastFocusedElement.focus === "function") {
      lastFocusedElement.focus();
    }
  }

  function handleAction(action, trigger) {
    if (action === "accept") {
      acceptAll();
    } else if (action === "reject") {
      rejectOptional();
    } else if (action === "save") {
      persistConsent(getSelectedConsent());
    } else if (action === "settings") {
      openDialog(trigger);
    }
  }

  document.addEventListener("click", function (event) {
    var actionButton = event.target.closest("[data-cookie-action]");
    if (actionButton) {
      handleAction(actionButton.getAttribute("data-cookie-action"), actionButton);
      return;
    }

    var settingsButton = event.target.closest("[data-cookie-settings]");
    if (settingsButton) {
      openDialog(settingsButton);
      return;
    }

    if (event.target.closest("[data-cookie-close]")) {
      closeDialog();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !dialog.hidden) {
      closeDialog();
    }
  });

  var storedConsent = readConsent();
  if (storedConsent) {
    applyConsent(storedConsent);
  } else {
    banner.hidden = false;
  }

  window.EveMapsCookieConsent = {
    get: function () { return readConsent() || defaultConsent(); },
    open: function () { openDialog(); }
  };
}());
