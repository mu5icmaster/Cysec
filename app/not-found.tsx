import Button from "./_components/Button";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Page not found",
};

function Error() {
  return (
    <div className="flex flex-col gap-6 py-24">
      <h1 className="text-center text-4xl font-bold uppercase tracking-wider text-red-600 sm:text-5xl">
        Ooops...
      </h1>
      <p className="text-center text-xl text-gray-700 sm:text-2xl">
        This page could not be found :(
      </p>
      <div className="flex justify-center">
        <Button type="primary" link="/">
          GO BACK
        </Button>
      </div>
    </div>
  );
}

export default Error;
