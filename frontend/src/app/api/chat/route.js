export async function POST(request) {
  try {
    const token = request.headers.get("authorization");

    if (!token) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    const body = await request.json();
    const { file_id, question } = body;

    if (!file_id || !question) {
      return new Response(
        JSON.stringify({ error: "Missing file_id or question" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        Authorization: token,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ file_id: file_id, question }),
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
