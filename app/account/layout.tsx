import AccountMenu from "../_components/AccountMenu";

function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="mx-auto mt-8 max-w-[1600px] px-4 md:mt-16 lg:px-8">
      <h2 className="text-center text-4xl font-bold text-gray-700 md:text-left dark:text-gray-200">
        Account
      </h2>
      <section className="grid h-full gap-4 py-4 md:grid-cols-[1fr_2fr] lg:grid-cols-[1fr_2.5fr] lg:gap-16">
        <div className="flex h-full flex-col">
          <AccountMenu />
        </div>
        <div className="mt-2">{children}</div>
      </section>
    </div>
  );
}

export default Layout;
