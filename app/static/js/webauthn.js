export async function startRegistration(opts) {
	const credential = await navigator.credentials.create({
		publicKey: opts,
	});
	return credential;
}

export async function sendRegistrationResponse(credential) {
	const resp = await fetch("/verify-registration-response", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(credential),
	});
	return resp;
}