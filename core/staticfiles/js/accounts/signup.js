function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length === 2) {
    return parts.pop().split(";").shift();
  }
  return "";
}

function normalizeErrors(payload) {
  if (!payload) {
    return ["Signup failed. Please try again."];
  }
  if (typeof payload === "string") {
    return [payload];
  }
  if (Array.isArray(payload)) {
    return payload;
  }
  if (typeof payload === "object") {
    var messages = [];
    Object.keys(payload).forEach(function (key) {
      var value = payload[key];
      if (Array.isArray(value)) {
        messages.push(key + ": " + value.join(", "));
      } else if (value) {
        messages.push(key + ": " + value);
      }
    });
    if (messages.length) {
      return messages;
    }
  }
  return ["Signup failed. Please try again."];
}

function showErrors(messages) {
  var errorsBox = document.getElementById("signup-errors");
  errorsBox.innerHTML = "";
  if (!messages || !messages.length) {
    errorsBox.style.display = "none";
    return;
  }
  var list = document.createElement("ul");
  messages.forEach(function (msg) {
    var item = document.createElement("li");
    item.textContent = msg;
    list.appendChild(item);
  });
  errorsBox.appendChild(list);
  errorsBox.style.display = "block";
}

function showSuccess(message) {
  var successBox = document.getElementById("signup-success");
  successBox.textContent = message || "";
  if (message) {
    successBox.style.display = "block";
  } else {
    successBox.style.display = "none";
  }
}

window.addEventListener("load", function () {
  var signupForm = document.getElementById("signup-form");
  if (!signupForm) {
    return;
  }

  signupForm.addEventListener("submit", function (event) {
    event.preventDefault();
    showErrors([]);
    showSuccess("");

    var data = new URLSearchParams();
    data.append("email", signupForm.email.value);
    data.append("password", signupForm.password.value);
    data.append("password1", signupForm.password1.value);
    var captchaToken = "";
    if (window.grecaptcha) {
      captchaToken = window.grecaptcha.getResponse();
    }
    if (!captchaToken) {
      showErrors(["Please complete the CAPTCHA."]);
      return;
    }
    data.append("g-recaptcha-response", captchaToken);

    fetch(signupForm.action, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: data
    }).then(function (response) {
      return response.json().then(function (payload) {
        return { ok: response.ok, payload: payload };
      });
    }).then(function (result) {
      if (result.ok) {
        showSuccess("Account created. Check your email to activate.");
        signupForm.reset();
        if (window.grecaptcha) {
          window.grecaptcha.reset();
        }
      } else {
        showErrors(normalizeErrors(result.payload));
        if (window.grecaptcha) {
          window.grecaptcha.reset();
        }
      }
    }).catch(function () {
      showErrors(["Signup failed. Please try again."]);
      if (window.grecaptcha) {
        window.grecaptcha.reset();
      }
    });
  });
});
