import { Space } from 'antd'
import WalletConfig from './WalletConfig'
import UrlConfig from './UrlConfig'
import ProxyConfig from './ProxyConfig'

export default function Config() {
    return (
        <Space.Compact >
            <UrlConfig />
            <ProxyConfig />
            <WalletConfig />
        </Space.Compact>
    )
}

