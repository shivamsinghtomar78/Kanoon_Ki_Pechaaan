/**
 * Authentication JavaScript
 * Handles login, registration, and auth-related functionality
 */

const Auth = {
    // Login user
    async login(email, password) {
        try {
            Utils.showLoading();
            
            const response = await API.post('/auth/login', {
                email: email,
                password: password
            });
            
            if (response.success) {
                window.currentUser = response.user;
                Utils.showAlert('Login successful! Redirecting...', 'success', 2000);
                
                // Redirect after short delay
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                Utils.showAlert(response.message || 'Login failed', 'danger');
            }
        } catch (error) {
            Utils.showAlert(error.message || 'Login failed. Please try again.', 'danger');
        } finally {
            Utils.hideLoading();
        }
    },

    // Register user
    async register(userData) {
        try {
            Utils.showLoading();
            
            const response = await API.post('/auth/register', userData);
            
            if (response.success) {
                window.currentUser = response.user;
                Utils.showAlert('Registration successful! Redirecting...', 'success', 2000);
                
                // Redirect after short delay
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                Utils.showAlert(response.message || 'Registration failed', 'danger');
            }
        } catch (error) {
            Utils.showAlert(error.message || 'Registration failed. Please try again.', 'danger');
        } finally {
            Utils.hideLoading();
        }
    },

    // Change password
    async changePassword(currentPassword, newPassword) {
        try {
            Utils.showLoading();
            
            const response = await API.put('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword
            });
            
            if (response.success) {
                Utils.showAlert('Password changed successfully!', 'success');
                return true;
            } else {
                Utils.showAlert(response.message || 'Failed to change password', 'danger');
                return false;
            }
        } catch (error) {
            Utils.showAlert(error.message || 'Failed to change password', 'danger');
            return false;
        } finally {
            Utils.hideLoading();
        }
    },

    // Update profile
    async updateProfile(profileData) {
        try {
            Utils.showLoading();
            
            const response = await API.put('/auth/profile', profileData);
            
            if (response.success) {
                window.currentUser = response.user;
                Session.updateNavbar(response.user);
                Utils.showAlert('Profile updated successfully!', 'success');
                return true;
            } else {
                Utils.showAlert(response.message || 'Failed to update profile', 'danger');
                return false;
            }
        } catch (error) {
            Utils.showAlert(error.message || 'Failed to update profile', 'danger');
            return false;
        } finally {
            Utils.hideLoading();
        }
    }
};

// Login Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear previous validation
            FormHelpers.clearValidation(this);
            
            // Get form data
            const formData = new FormData(this);
            const email = formData.get('email');
            const password = formData.get('password');
            
            // Validate inputs
            let isValid = true;
            
            if (!email) {
                FormHelpers.showFieldError(this.email, 'Email is required');
                isValid = false;
            } else if (!Utils.validateEmail(email)) {
                FormHelpers.showFieldError(this.email, 'Please enter a valid email');
                isValid = false;
            }
            
            if (!password) {
                FormHelpers.showFieldError(this.password, 'Password is required');
                isValid = false;
            }
            
            if (isValid) {
                await Auth.login(email, password);
            }
        });
    }
});

// Registration Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear previous validation
            FormHelpers.clearValidation(this);
            
            // Get form data
            const formData = new FormData(this);
            const userData = {
                name: formData.get('name'),
                email: formData.get('email'),
                password: formData.get('password'),
                user_type: formData.get('user_type') || 'user',
                phone_no: formData.get('phone_no'),
                degree: formData.get('degree'),
                college: formData.get('college'),
                qualifications: formData.get('qualifications')
            };
            
            const confirmPassword = formData.get('confirm_password');
            
            // Validate inputs
            let isValid = true;
            
            if (!userData.name) {
                FormHelpers.showFieldError(this.name, 'Name is required');
                isValid = false;
            }
            
            if (!userData.email) {
                FormHelpers.showFieldError(this.email, 'Email is required');
                isValid = false;
            } else if (!Utils.validateEmail(userData.email)) {
                FormHelpers.showFieldError(this.email, 'Please enter a valid email');
                isValid = false;
            }
            
            if (!userData.password) {
                FormHelpers.showFieldError(this.password, 'Password is required');
                isValid = false;
            } else {
                const passwordValidation = Utils.validatePassword(userData.password);
                if (!passwordValidation.valid) {
                    FormHelpers.showFieldError(this.password, passwordValidation.message);
                    isValid = false;
                }
            }
            
            if (userData.password !== confirmPassword) {
                FormHelpers.showFieldError(this.confirm_password, 'Passwords do not match');
                isValid = false;
            }
            
            // Validate terms checkbox
            const termsCheckbox = this.querySelector('input[name="terms"]');
            if (termsCheckbox && !termsCheckbox.checked) {
                Utils.showAlert('Please agree to the Terms and Conditions', 'warning');
                isValid = false;
            }
            
            if (isValid) {
                await Auth.register(userData);
            }
        });
        
        // User type change handler
        const userTypeSelect = registerForm.querySelector('select[name="user_type"]');
        if (userTypeSelect) {
            userTypeSelect.addEventListener('change', function() {
                const lawyerFields = registerForm.querySelector('#lawyerFields');
                if (lawyerFields) {
                    if (this.value === 'lawyer') {
                        lawyerFields.style.display = 'block';
                    } else {
                        lawyerFields.style.display = 'none';
                    }
                }
            });
        }
    }
});

// Profile Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear previous validation
            FormHelpers.clearValidation(this);
            
            // Get form data
            const formData = new FormData(this);
            const profileData = {
                name: formData.get('name'),
                phone_no: formData.get('phone_no'),
                degree: formData.get('degree'),
                college: formData.get('college'),
                qualifications: formData.get('qualifications'),
                social_media: formData.get('social_media')
            };
            
            // Validate inputs
            let isValid = true;
            
            if (!profileData.name) {
                FormHelpers.showFieldError(this.name, 'Name is required');
                isValid = false;
            }
            
            if (isValid) {
                const success = await Auth.updateProfile(profileData);
                if (success) {
                    // Optionally reload the page or update the form
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                }
            }
        });
    }
});

// Change Password Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear previous validation
            FormHelpers.clearValidation(this);
            
            // Get form data
            const formData = new FormData(this);
            const currentPassword = formData.get('current_password');
            const newPassword = formData.get('new_password');
            const confirmPassword = formData.get('confirm_password');
            
            // Validate inputs
            let isValid = true;
            
            if (!currentPassword) {
                FormHelpers.showFieldError(this.current_password, 'Current password is required');
                isValid = false;
            }
            
            if (!newPassword) {
                FormHelpers.showFieldError(this.new_password, 'New password is required');
                isValid = false;
            } else {
                const passwordValidation = Utils.validatePassword(newPassword);
                if (!passwordValidation.valid) {
                    FormHelpers.showFieldError(this.new_password, passwordValidation.message);
                    isValid = false;
                }
            }
            
            if (newPassword !== confirmPassword) {
                FormHelpers.showFieldError(this.confirm_password, 'Passwords do not match');
                isValid = false;
            }
            
            if (isValid) {
                const success = await Auth.changePassword(currentPassword, newPassword);
                if (success) {
                    // Clear form
                    this.reset();
                }
            }
        });
    }
});

// Real-time validation
document.addEventListener('DOMContentLoaded', function() {
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !Utils.validateEmail(this.value)) {
                FormHelpers.showFieldError(this, 'Please enter a valid email address');
            } else if (this.value) {
                FormHelpers.showFieldSuccess(this);
            }
        });
    });
    
    // Password validation
    const passwordInputs = document.querySelectorAll('input[type="password"][name="password"], input[type="password"][name="new_password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                const validation = Utils.validatePassword(this.value);
                if (!validation.valid) {
                    FormHelpers.showFieldError(this, validation.message);
                } else {
                    FormHelpers.showFieldSuccess(this);
                }
            }
        });
    });
    
    // Confirm password validation
    const confirmPasswordInputs = document.querySelectorAll('input[name="confirm_password"]');
    confirmPasswordInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const passwordInput = this.form.querySelector('input[type="password"]:not([name="confirm_password"])');
            if (this.value && passwordInput && this.value !== passwordInput.value) {
                FormHelpers.showFieldError(this, 'Passwords do not match');
            } else if (this.value && passwordInput && this.value === passwordInput.value) {
                FormHelpers.showFieldSuccess(this);
            }
        });
    });
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Auth;
}