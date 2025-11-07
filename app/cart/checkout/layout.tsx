"use client";

function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <div className="mx-auto mt-8 max-w-[1300px] px-4">{children}</div>;
}

export default Layout;
