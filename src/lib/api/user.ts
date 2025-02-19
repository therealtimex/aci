export async function checkSignUpCode(signup_code: string): Promise<boolean> {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/auth/validate-signup-code/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ signup_code }),
    });

    return response.ok;
}
