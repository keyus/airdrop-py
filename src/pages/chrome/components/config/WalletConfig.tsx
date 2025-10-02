import { useContext, useMemo } from 'react';
import { Button, Input, Form, Modal, } from 'antd';
import { useBoolean, } from 'ahooks';
import { ConfigContext } from '@/rootContext';

export default function WalletConfig() {
    const [form] = Form.useForm();
    const { config, updateConfig, } = useContext(ConfigContext);
    const [open, { toggle }] = useBoolean();
    const walletValue = Form.useWatch('wallet', form);
    const onSubmit = async ({ wallet }) => {
        if (wallet) {
            wallet = wallet.split('\n')
            wallet = wallet.map((item: string) => item.trim()).filter((item: string) => item)
        } else {
            wallet = []
        }
        await updateConfig({ ...config, wallet })
        toggle()
    }
    const walletlens = useMemo(() => {
        if (Array.isArray(walletValue)) {
            return walletValue.length
        } else {
            return walletValue?.split('\n').length || 0
        }
    }, [walletValue])

    return (
        <>
            <Button size='large' onClick={toggle}>钱包配置</Button>
            <Modal
                title='钱包配置'
                open={open}
                destroyOnHidden
                mask={false}
                onCancel={toggle}
                onOk={form.submit}
            >
                <Form
                    form={form}
                    layout='vertical'
                    onFinish={onSubmit}
                    initialValues={{
                        wallet: config.wallet.join('\n'),
                    }}
                >
                    <Form.Item
                        name='wallet'
                        rules={[{ required: true, message: '请输入钱包配置' }]}
                        extra={`当前钱包数量：${walletlens}`}
                    >
                        <Input.TextArea rows={10} />
                    </Form.Item>
                </Form>
            </Modal>
        </>
    )
}
