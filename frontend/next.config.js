/** @type {import('next').NextConfig} */
if (process.env.NODE_ENV === "production" && !process.env.NEXT_PUBLIC_API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL must be set for production builds.");
}

const nextConfig = {
  reactStrictMode: true,
  allowedDevOrigins: ["http://localhost:3000", "http://127.0.0.1:3000"],
  async rewrites() {
    if (process.env.NODE_ENV === "production" || process.env.NEXT_PUBLIC_API_URL) {
      return [];
    }

    return [
      {
        source: "/api/v1/:path*",
        destination: "http://127.0.0.1:8000/api/v1/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
