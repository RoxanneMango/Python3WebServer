const loginForm = document.getElementById("login-form");
const loginButton = document.getElementById("login-form-submit");
const loginErrorMsg = document.getElementById("login-error-msg");

loginButton.addEventListener("click", (e) => {
    e.preventDefault();
    const username = loginForm.username.value;
    const password = loginForm.password.value;
	
	let url = "/login";
	let data = {
		"username": username,
		"password": password
	}

	let response = fetch(url, {method: 'POST', body: JSON.stringify(data)})
	.then(response => response.text())
	.then(response => {
		console.log(response);
		
		if(response.length == 32 && !response.includes(' ')) {
			window.location.reload();
		}
		else {
			loginErrorMsg.style.opacity = 1;
		}		
		
		
		/*
		
		// Get the current data-time stamp
		let date = new Date();
		// Set expiration date to be one week from now;
		let time = date.getTime();
		let min = 60;
		let hour = min * 60;
		let day = hour * 24;
		let week = day * 7;
		time += 1*week*1000;
		date.setTime(time);
//		console.log(date.toString());
		// Name of cookie
		let usernameCookie = "matrics_username";
		let sessionHashCookie = "matrics_sessionHash";
		// Only set the cookie if a session hash was sent back
		if(response.length == 32 && !response.includes(' ')) {
			// Set sessionHash cookie
//			document.cookie = usernameCookie+"="+username+"; expires="+date.toString();
//			document.cookie = sessionHashCookie+"="+response+"; expires="+date.toString();
		}
		else {
			// Clearing sessionHash cookie
//			cookieStore.delete(usernameCookie);
//			cookieStore.delete(sessionHashCookie);
		}
		
		*/
		
		let x = document.cookie;
		console.log(x);
	})
	.catch(error => console.log(error));

})