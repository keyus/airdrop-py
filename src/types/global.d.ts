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
          start: () => Promise<{success: boolean, message?: string, error?: string}>
          add_instance: (name: string, profile_name?: string, proxy?: string) => Promise<{success: boolean, message?: string, error?: string}>
          remove_instance: (name: string) => Promise<{success: boolean, message?: string, error?: string}>
          navigate_instance: (instance_name: string, url: string) => Promise<{success: boolean, message?: string, error?: string}>
          navigate_all: (url: string) => Promise<{success: boolean, results?: any, error?: string}>
          click_element: (instance_name: string, selector: string) => Promise<{success: boolean, message?: string, error?: string}>
          input_text: (instance_name: string, selector: string, text: string) => Promise<{success: boolean, message?: string, error?: string}>
          get_page_title: (instance_name: string) => Promise<{success: boolean, title?: string, error?: string}>
          take_screenshot: (instance_name: string) => Promise<{success: boolean, screenshot?: string, error?: string}>
          get_status: () => Promise<{
            success: boolean
            data?: {
              total_instances: number
              running_instances: number
              instances: Record<string, {
                name: string
                port: number
                status: string
                profile: string
                proxy?: string
              }>
            }
            error?: string
          }>
          execute_batch: (task_config: {
            instances: string[]
            actions: Array<{
              type: string
              params: Record<string, any>
            }>
          }) => Promise<{success: boolean, results?: any, error?: string}>
          shutdown: () => Promise<{success: boolean, message?: string, error?: string}>
        }
      }
    }
    py: typeof window.pywebview.api;
    message: typeof import('antd/es/message').default;
  }
}
export { }