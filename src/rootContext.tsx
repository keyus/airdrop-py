import { createContext } from "react";

interface State {
    config: AppConfig;
    refreshConfig: () => void;
    updateConfig: (newConfig: AppConfig) => Promise<any>;
    loading: boolean
}

export const initConfigValue = {
    chrome_install_dir: '',
    chrome_user_data_dir: '',
    telegram_install_dir: '',
    use_url: false,
    url: [],
    use_proxy: false,
    wallet: [],
}


export const ConfigContext = createContext<State>(null); 