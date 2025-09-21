import { useContext } from 'react'
import { Button, Modal, Tabs, } from 'antd'
import { useBoolean, } from 'ahooks';
import { ConfigContext } from '@/rootContext';
import WalletConfig from './WalletConfig'
import UrlConfig from './UrlConfig'
import ProxyConfig from './ProxyConfig'

export default function Config() {
    const [open, { toggle }] = useBoolean();
    const { refreshConfig, } = useContext(ConfigContext);
    const onOk = () => {
        refreshConfig();
        toggle()
    }
    return (
        <>
            <Button
                size='large'
                onClick={toggle}
            >
                环境配置
            </Button>
            <Modal
                title='环境配置'
                open={open}
                destroyOnHidden
                mask={false}
                onCancel={toggle}
                footer={null}
            >
                <Tabs
                    items={[
                        {
                            key: 'url',
                            label: '启动网址',
                            children: <UrlConfig onOk={onOk} />
                        },
                        {
                            key: 'proxy',
                            label: '代理配置',
                            children: <ProxyConfig onOk={onOk} />
                        },
                        {
                            key: 'wallet',
                            label: '钱包配置',
                            children: <WalletConfig onOk={onOk} />
                        },
                    ]}
                />
            </Modal>
        </>
    )
}

