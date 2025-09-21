
import {createContext} from 'react'

export const rootContent = createContext<{
    config: AppConfig;
    updateConfig: (data: AppConfig)=>void;
}>(null);