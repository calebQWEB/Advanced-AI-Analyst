export async function POST(request, { params }) {
  try {
    const id = params.id;
    const token = request.headers.get("authorization");
    if (!token || !id) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    const response = await fetch(
      `https://advanced-ai-analyst.onrender.com/export/pdf/${id}`,
      {
        method: "POST",
        headers: {
          Authorization: token,
          Accept: "application/pdf",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const pdfBuffer = await response.arrayBuffer();

    // Get the filename from the backend response headers
    const contentDisposition = response.headers.get("content-disposition");

    return new Response(pdfBuffer, {
      headers: {
        "Content-Type": "application/pdf",
        // Pass through the content-disposition header if it exists
        ...(contentDisposition && {
          "Content-Disposition": contentDisposition,
        }),
      },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
