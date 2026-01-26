// Simple test to verify JWT token decoding logic
function testJwtDecoding() {
  // Example JWT token (this is a fake one for testing)
  const fakeToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";

  try {
    const parts = fakeToken.split('.');
    if (parts.length === 3) {
      // Decode the payload (second part)
      const payload = parts[1];
      // Add padding if needed
      const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
      const decoded = JSON.parse(atob(paddedPayload));
      console.log("Decoded JWT payload:", decoded);
    } else {
      console.log("Not a standard JWT format");
    }
  } catch (e) {
    console.error("Error decoding token", e);
  }
}

testJwtDecoding();

// Test token that's not a JWT
const nonJwtToken = "abc123def456";
try {
  const parts = nonJwtToken.split('.');
  if (parts.length === 3) {
    console.log("This looks like a JWT");
  } else {
    console.log("This is not a JWT, parts:", parts.length);
  }
} catch (e) {
  console.error("Error with non-JWT token", e);
}