document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const formSteps = document.querySelectorAll(".form-step")
  const progressSteps = document.querySelectorAll(".step")
  const progressLines = document.querySelectorAll(".progress-line")
  const themeToggle = document.getElementById("themeToggle")

  // Form Navigation Buttons
  const step1Next = document.getElementById("step1Next")
  const step2Back = document.getElementById("step2Back")
  const step2Next = document.getElementById("step2Next")
  const step3Back = document.getElementById("step3Back")
  const submitForm = document.getElementById("submitForm")

  // Current active step (1-indexed)
  let currentStep = 1

  // Theme toggle functionality
  if (themeToggle) {
    themeToggle.addEventListener("change", function () {
      if (this.checked) {
        document.body.classList.add("dark-mode")
        localStorage.setItem("theme", "dark")
      } else {
        document.body.classList.remove("dark-mode")
        localStorage.setItem("theme", "light")
      }
    })

    // Check for saved theme preference
    const savedTheme = localStorage.getItem("theme")
    if (savedTheme === "dark") {
      document.body.classList.add("dark-mode")
      themeToggle.checked = true
    }
  }

  // Display specific step
  const showStep = (stepNumber) => {
    formSteps.forEach((step, index) => {
      step.classList.remove("active")

      if (index + 1 === stepNumber) {
        step.classList.add("active")
      }
    })

    // Update progress bar
    progressSteps.forEach((step, index) => {
      step.classList.remove("active", "completed")

      if (index + 1 === stepNumber) {
        step.classList.add("active")
      } else if (index + 1 < stepNumber) {
        step.classList.add("completed")
      }
    })

    // Update progress lines
    progressLines.forEach((line, index) => {
      line.classList.remove("active")

      if (index + 1 < stepNumber) {
        line.classList.add("active")
      }
    })

    currentStep = stepNumber
  }

  // Form Validation Functions
  const validateStep1 = () => {
    let isValid = true
    const firstName = document.getElementById("id_first_name")
    const lastName = document.getElementById("id_last_name")
    const dob = document.getElementById("id_date_of_birth")
    const genderRadios = document.querySelectorAll('input[name="gender"]')

    // First Name validation
    if (!firstName.value.trim()) {
      showError(firstName, "First name is required")
      isValid = false
    } else {
      clearError(firstName)
    }

    // Last Name validation
    if (!lastName.value.trim()) {
      showError(lastName, "Last name is required")
      isValid = false
    } else {
      clearError(lastName)
    }

    // Date of Birth validation
    if (!dob.value) {
      showError(dob, "Date of birth is required")
      isValid = false
    } else {
      clearError(dob)
    }

    // Gender validation
    let genderSelected = false
    genderRadios.forEach((radio) => {
      if (radio.checked) genderSelected = true
    })

    if (!genderSelected) {
      const genderField = document.querySelector(".radio-group")
      const errorMsg = document.createElement("div")
      errorMsg.className = "error-message"
      errorMsg.textContent = "Please select a gender"

      // Remove any existing error message
      const existingError = genderField.parentNode.querySelector(".error-message")
      if (existingError) existingError.remove()

      genderField.parentNode.appendChild(errorMsg)
      isValid = false
    } else {
      const genderField = document.querySelector(".radio-group")
      const existingError = genderField.parentNode.querySelector(".error-message")
      if (existingError) existingError.remove()
    }

    return isValid
  }

  const validateStep2 = () => {
    let isValid = true
    const email = document.getElementById("id_email")
    const phone = document.getElementById("id_phone")
    const address = document.getElementById("id_address")

    // Email validation
    if (!email.value.trim()) {
      showError(email, "Email is required")
      isValid = false
    } else if (!isValidEmail(email.value)) {
      showError(email, "Please enter a valid email address")
      isValid = false
    } else {
      clearError(email)
    }

    // Phone validation
    if (!phone.value.trim()) {
      showError(phone, "Phone number is required")
      isValid = false
    } else if (!isValidPhone(phone.value)) {
      showError(phone, "Please enter a valid phone number")
      isValid = false
    } else {
      clearError(phone)
    }

    // Address validation
    if (!address.value.trim()) {
      showError(address, "Address is required")
      isValid = false
    } else {
      clearError(address)
    }

    return isValid
  }

  // Helper functions for validation
  const showError = (input, message) => {
    const formGroup = input.closest(".form-group")
    let errorElement = formGroup.querySelector(".error-message")

    if (!errorElement) {
      errorElement = document.createElement("div")
      errorElement.className = "error-message"
      formGroup.appendChild(errorElement)
    }

    input.classList.add("is-invalid")
    errorElement.textContent = message
  }

  const clearError = (input) => {
    const formGroup = input.closest(".form-group")
    const errorElement = formGroup.querySelector(".error-message")

    input.classList.remove("is-invalid")
    if (errorElement) {
      errorElement.textContent = ""
    }
  }

  const isValidEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
  }

  const isValidPhone = (phone) => {
    const re = /^\d{10,15}$/
    return re.test(phone.replace(/[^0-9]/g, ""))
  }

  // Update summary
  const updateSummary = () => {
    const firstName = document.getElementById("id_first_name").value
    const middleName = document.getElementById("id_middle_name").value
    const lastName = document.getElementById("id_last_name").value
    const dob = document.getElementById("id_date_of_birth").value
    const gender = document.querySelector('input[name="gender"]:checked')?.value
    const email = document.getElementById("id_email").value
    const phone = document.getElementById("id_phone").value
    const address = document.getElementById("id_address").value

    // Format full name
    let fullName = firstName
    if (middleName) fullName += " " + middleName
    fullName += " " + lastName

    // Format date
    const formattedDate = dob
      ? new Date(dob).toLocaleDateString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
        })
      : ""

    // Format gender
    const formattedGender = gender ? gender.charAt(0).toUpperCase() + gender.slice(1) : ""

    // Update summary fields
    document.getElementById("summaryName").textContent = fullName
    document.getElementById("summaryDob").textContent = formattedDate
    document.getElementById("summaryGender").textContent = formattedGender
    document.getElementById("summaryEmail").textContent = email
    document.getElementById("summaryPhone").textContent = phone
    document.getElementById("summaryAddress").textContent = address
  }

  // Event Listeners
  if (step1Next) {
    step1Next.addEventListener("click", () => {
      if (validateStep1()) {
        showStep(2)
      }
    })
  }

  if (step2Back) {
    step2Back.addEventListener("click", () => {
      showStep(1)
    })
  }

  if (step2Next) {
    step2Next.addEventListener("click", () => {
      if (validateStep2()) {
        updateSummary()
        showStep(3)
      }
    })
  }

  if (step3Back) {
    step3Back.addEventListener("click", () => {
      showStep(2)
    })
  }

  // Initialize the form
  showStep(1)
})

