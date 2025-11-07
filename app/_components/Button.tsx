import Link from "next/link";
import { ReactNode, RefObject } from "react";
import { Button as ButtonCn } from "@/app/_components/ButtonCn";

interface ButtonComponentProps {
  type: "primary" | "secondary";
  link?: string;
  onClick?: () => void;
  children: ReactNode;
  disabled?: boolean;
  ref?: RefObject<HTMLButtonElement | null>;
}

function Button({
  type,
  link,
  onClick,
  children,
  disabled,
  ref,
}: ButtonComponentProps) {
  if (type === "primary" && link)
    return (
      <ButtonCn asChild size="lg">
        <Link href={link}>{children}</Link>
      </ButtonCn>
    );

  if (type === "primary" && !link)
    return (
      <ButtonCn size="lg" onClick={onClick} disabled={disabled} ref={ref}>
        {children}
      </ButtonCn>
    );

  if (type === "secondary" && link)
    return (
      <Link
        href={link}
        className="relative px-0.5 pb-[0.1rem] pt-1 font-semibold text-gray-500 transition-colors duration-100 after:absolute after:block after:h-[2px] after:w-full after:origin-center after:scale-x-0 after:bg-gray-500 after:transition after:duration-300 after:content-[''] after:hover:scale-x-100"
      >
        {children}
      </Link>
    );
  if (type === "secondary" && !link)
    return (
      <button
        onClick={onClick}
        disabled={disabled}
        className="relative px-0.5 pb-[0.1rem] pt-1 font-semibold text-gray-500 transition-colors duration-100 after:absolute after:block after:h-[2px] after:w-full after:origin-center after:scale-x-0 after:bg-gray-500 after:transition after:duration-300 after:content-[''] after:hover:scale-x-100"
      >
        {children}
      </button>
    );
}

export default Button;
