import Image from "next/image";
import Button from "./Button";
import heroimg from "@/public/hero.jpg";

function Hero() {
  return (
    <section className="flex justify-center bg-gray-200/90 dark:bg-gray-800">
      <div className="mx-4 grid w-full max-w-[1200px] grid-cols-1 place-items-center justify-center justify-items-center py-12 md:grid-cols-[1fr_1fr] md:gap-16 md:py-16">
        <div className="flex flex-col items-center gap-2">
          <h2 className="px-2 text-center text-5xl font-bold text-gray-700 dark:text-gray-300 sm:text-6xl lg:text-7xl">
            <span className="text-nowrap">SAVE UP TO</span> 50%
          </h2>
          <p className="w-full text-nowrap text-center text-lg font-[600] text-gray-600 dark:text-gray-300 sm:text-xl lg:text-2xl lg:font-normal">
            Limited time offers on best-selling items
          </p>
          <Button type="primary" link="/products">
            SEE OFFER
          </Button>
        </div>
        <div className="mt-4 flex w-full justify-center md:mt-0">
          <Image
            src={heroimg}
            width={400}
            height={400}
            placeholder="blur"
            alt="nintendo console"
            className="w-3/4 rounded-lg shadow-md dark:grayscale-[10%] md:w-auto"
          />
        </div>
      </div>
    </section>
  );
}

export default Hero;
