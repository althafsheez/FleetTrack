import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1", "localhost", "192.168.1.39"],
  async rewrites() {
    return [{
      source: "/api/:path*",
      destination: `${process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000"}/:path*`,
    }];
  },
};

export default nextConfig;
