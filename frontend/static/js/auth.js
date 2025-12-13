document.addEventListener('DOMContentLoaded', () => {
    const togglePanel           = document.querySelector('.toggle')
    const toggleButtons         = document.querySelectorAll('.toggle button')
    const identifierInput       = document.getElementById('identifier')
    const usernameInput         = document.getElementById('username')
    const emailInput            = document.getElementById('email')
    const passwordInput         = document.getElementById('password')
    const submitButton          = document.getElementById('submit-btn')
    const authForm              = document.getElementById('form')
    const globalErrorElement    = document.querySelector('.global-error')
    const passwordRulesPanel    = document.querySelector('.password-rules')
    const passwordRuleElements   = passwordRulesPanel.querySelectorAll('div')

    const identifierField       = document.getElementById('identifier-field')
    const usernameField         = document.getElementById('username-field')
    const emailField            = document.getElementById('email-field')

    const clearErrors = () => {
        document.querySelectorAll('.field').forEach(field => field.classList.remove('error'))
        document.querySelectorAll('.error-msg').forEach(msg => msg.textContent = '')
        globalErrorElement.textContent = ''
        passwordRuleElements.forEach(el => el.classList.remove('valid', 'invalid'))
    }

    const validatePassword = () => {
        const value = passwordInput.value
        const rules = {
            length:  value.length >= 8,
            letter:  /[a-zA-Z]/.test(value),
            digit:   /\d/.test(value),
            special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(value)
        }

        passwordRuleElements.forEach(element => {
            const ruleName = element.dataset.rule
            element.classList.toggle('valid', rules[ruleName])
            element.classList.toggle('invalid', !rules[ruleName])
        })

        submitButton.disabled = !Object.values(rules).every(Boolean)
    }

    toggleButtons.forEach(button => button.addEventListener('click', () => {
        const isRegistration = button.dataset.mode === 'register'

        toggleButtons.forEach(btn => btn.classList.toggle('active', btn === button))
        togglePanel.classList.toggle('register', isRegistration)

        identifierField.classList.toggle('hidden', isRegistration)
        usernameField.classList.toggle('hidden', !isRegistration)
        emailField.classList.toggle('hidden', !isRegistration)
        passwordRulesPanel.classList.toggle('hidden', !isRegistration)

        identifierInput.required = !isRegistration
        usernameInput.required   = isRegistration
        emailInput.required      = isRegistration
        passwordInput.required    = true

        document.querySelectorAll('.field').forEach(field => {
            const input = field.querySelector('input')
            if (input) {
                input.disabled = field.classList.contains('hidden')
                input.required = !field.classList.contains('hidden')
            }
        })

        submitButton.textContent = isRegistration ? 'Sign up' : 'Sign in'
        submitButton.disabled = isRegistration

        clearErrors()
        if (isRegistration) validatePassword()
    }))

    passwordInput.addEventListener('input', () => {
        if (!passwordRulesPanel.classList.contains('hidden')) validatePassword()
    })

    authForm.addEventListener('submit', event => {
        event.preventDefault()
        clearErrors()

        const isRegistration = togglePanel.classList.contains('register')
        if (isRegistration && submitButton.disabled) return

        submitButton.disabled = true
        submitButton.textContent = 'Loading...'

        const url = isRegistration ? '/api/users/register' : '/api/users/login'

        const payload = { password: passwordInput.value }
        if (isRegistration) {
            payload.username = usernameInput.value
            payload.email    = emailInput.value
        } else {
            payload.username_or_email = identifierInput.value.trim()
        }

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            credentials: 'include'
        })
        .then(response => response.ok ? location.href = '/rooms' : response.json().then(err => { throw err }))
        .catch(error => {
            const message = error?.detail || 'Error'
            if (!isRegistration) {
                identifierField.classList.add('error')
                identifierField.querySelector('.error-msg').textContent = 'Incorrect username or password'
            } else if (message.toLowerCase().includes('username')) {
                usernameField.classList.add('error')
                usernameField.querySelector('.error-msg').textContent = 'Username already exists'
            } else if (message.toLowerCase().includes('email')) {
                emailField.classList.add('error')
                emailField.querySelector('.error-msg').textContent = 'Email already taken'
            } else {
                globalErrorElement.textContent = message
            }
        })
        .finally(() => {
            submitButton.disabled = isRegistration
            submitButton.textContent = isRegistration ? 'Sign up' : 'Sign in'
            if (isRegistration) validatePassword()
        })
    })
})