interface ConfigPromise {
  data: AppConfig;
  status: boolean;
}

interface ProcessResult {
  status: boolean;
  data: {
    chrome: {
      pid: number;
      name: string;
    }[];
    telegram: {
      pid: number;
      name: string;
    }[];
  }
}


declare global {
  interface Window {
    pywebview: {
      api: {
        app: {
          clear:()=>void;
          open_chrome: (names: string[]) => Promise<void>
          open_telegram: (names: string[]) => Promise<void>
          close_chrome: (names: string[]) => Promise<void>
          close_telegram: (names: string[] | string) => Promise<void>
          close_telegram_all: () => Promise<void>
          close_chrome_all: () => Promise<void>
          get_open: () => Promise<{
            chrome: {
              pid: number
              name: string
            }[]
            telegram: {
              pid: number
              name: string
            }[]
          }>
        }
        chrome_app: {
          install: (id: string) => Promise<any>
          uninstall: (id: string) => Promise<any>
        }
        config: {
          get_config: () => Promise<ConfigPromise>
          get_proxy: () => Promise<Record<string, any>>
          set_config: (config: Record<string, any>) => Promise<any>
          set_proxy: (proxy: string) => Promise<any>
        }
        clear_cache: () => Promise<void>
        webshare: {
          my_ip: () => Promise<any>
          get_ipauthorization: () => Promise<any>
          remove_ipauthorization: (id: number) => Promise<any>
          add_ipauthorization: (data: { ip_address: string }) => Promise<any>
          update_proxy: () => Promise<any>
        }
        sync: {
          start: () => Promise<{
            success: boolean
            message?: string
            master?: string
            total_instances?: number
            sync_enabled?: boolean
            error?: string
          }>
          stop: ()=>Promise<void>
          get_sync_status: ()=>Promise<{
            success: boolean
            data: boolean
          }>
        }
      }
    }
    py: typeof window.pywebview.api;
    message: typeof import('antd/es/message').default;
  }
}
export { }