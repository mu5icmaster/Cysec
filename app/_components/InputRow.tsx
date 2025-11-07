import { ReactNode } from "react";

function InputRow({ children }: { children: ReactNode }) {
  return <div className="flex flex-col gap-1">{children}</div>;
}

export default InputRow;
