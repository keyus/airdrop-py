import { useContext, useMemo } from 'react';
import { Button, Input, Form, } from 'antd';
import { ConfigContext } from '@/rootContext';


//钱包配置
interface Props {
    onOk: () => void
}

export default function WalletConfig({ onOk }: Props) {
    const [form] = Form.useForm();
    const { config, updateConfig } = useContext(ConfigContext);

    const walletValue = Form.useWatch('wallet', form);
    const onSubmit = async ({ wallet }) => {
        if (wallet) {
            wallet = wallet.split('\n')
            wallet = wallet.map((item: string) => item.trim()).filter((item: string) => item)
        } else {
            wallet = []
        }
        await updateConfig({ ...config, wallet })
        onOk()
    }
    const walletlens = useMemo(() => {
        if (Array.isArray(walletValue)) {
            return walletValue.length
        } else {
            return walletValue?.split('\n').length || 0
        }
    }, [walletValue])

    return (
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
            <Form.Item style={{ textAlign: 'right' }}>
                <Button
                    type='primary'
                    size='large'
                    onClick={() => {
                        form.submit()
                    }}
                >
                    保存钱包配置
                </Button>
            </Form.Item>
        </Form>
    )
}
