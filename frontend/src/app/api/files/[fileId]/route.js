export async function GET(request, { params }) {
  try {
    const fileId = await params.fileId;
    const token = request.headers.get("authorization");
    if (!token || !fileId) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    const response = await fetch(
      `https://advanced-ai-analyst.onrender.com/files/${fileId}`,
      {
        method: "GET",
        headers: {
          Authorization: token,
          Accept: "application/json",
        },
      }
    );

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

export async function DELETE(request, { params }) {
  try {
    const fileId = await params.fileId;
    const token = request.headers.get("authorization");
    if (!token || !fileId) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    const response = await fetch(
      `https://advanced-ai-analyst.onrender.com/files/${fileId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: token,
          Accept: "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return new Response(
      JSON.stringify({ message: "File deleted successfully" }),
      {
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
