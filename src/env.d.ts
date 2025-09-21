/// <reference types="antd/es/message/interface" />

declare module '*.svg' {
  export const ReactComponent: React.FunctionComponent<
    React.SVGProps<SVGSVGElement>
  >;
  const content: string;
  export default content;
}
declare module '*.svg?react' {
  const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  export default ReactComponent;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

interface AppConfig {
  chrome_install_dir?: string;
  chrome_user_data_dir?: string;
  telegram_install_dir?: string;
  use_url?: boolean;
  url?: string[];
  use_proxy?: boolean;
  wallet?: string[];
}