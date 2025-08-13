export async function POST(request) {
  try {
    const token = request.headers.get("authorization");

    if (!token) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Get FormData from the request
    const formData = await request.formData();
    const file = formData.get("file");

    if (!file) {
      return new Response(JSON.stringify({ error: "No file uploaded" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Forward the FormData to your FastAPI backend
    const backendFormData = new FormData();
    backendFormData.append("file", file);

    const response = await fetch("http://localhost:8000/upload", {
      method: "POST",
      headers: {
        Authorization: token,
        // Don't set Content-Type manually for FormData
      },
      body: backendFormData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
