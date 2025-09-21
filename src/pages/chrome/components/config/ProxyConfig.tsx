import { useMemo, useState, useContext } from 'react'
import { Button, Input, Form, Switch, } from 'antd'
import { ConfigContext } from '@/rootContext';
import { useMount, } from 'ahooks';
import IpAuth from './IpAuth';


//代理配置
export default function ProxyConfig(props: { onOk: () => void }) {
    const { onOk, } = props;
    const { config, updateConfig } = useContext(ConfigContext);
    const [form] = Form.useForm();
    const [updateLoading, setUpdateLoading] = useState(false);
    const proxyValue = Form.useWatch('proxy', form)
    const onSubmit = async ({ proxy, use_proxy }) => {
        if (proxy) {
            proxy = proxy.split('\n')
            proxy = proxy.map((item: string) => item.trim()).filter((item: string) => item)
        } else {
            proxy = []
        }
        await window.py.config.set_proxy(proxy)
        await updateConfig({ ...config, use_proxy, })
        onOk()
    }

    // 获取代理列表
    const initData = async () => {
        const proxy: any = await window.py.config.get_proxy();
        form.setFieldsValue({
            proxy: proxy.data?.join('\n'),
        })
    }

    useMount(() => {
        initData()
    })

    const lens = useMemo(() => {
        if (Array.isArray(proxyValue)) {
            return proxyValue?.filter(it => it).length
        } else {
            return proxyValue?.split('\n').filter((it: any) => it).length || 0
        }
    }, [proxyValue])

    const updateProxy = async () => {
        setUpdateLoading(true);
        const res = await window.py.webshare.update_proxy()
        window.message.success('代理更新成功');
        initData();
        setUpdateLoading(false);
    }

    return (
        <>
            <Form
                name='proxyConfig'
                form={form}
                onFinish={onSubmit}
                initialValues={{
                    use_proxy: config.use_proxy || false,
                }}
            >
                <Form.Item
                    name='proxy'
                    extra={
                        <div>
                            当前有效的代理数量：{lens}
                            <Button
                                type='link'
                                loading={updateLoading}
                                onClick={updateProxy}>一键更新代理</Button>
                        </div>
                    }
                >
                    <Input.TextArea rows={8} />
                </Form.Item>
                <Form.Item
                    label='是否启用'
                    name='use_proxy'
                >
                    <Switch checkedChildren='启用' unCheckedChildren='禁用' />
                </Form.Item>

                <Form.Item
                    label='Ip授权'
                >
                    <IpAuth />
                </Form.Item>
                <Form.Item
                    style={{ textAlign: 'right' }}
                >
                    <Button
                        type='primary'
                        htmlType='submit'
                        size='large'
                    >
                        保存代理配置
                    </Button>
                </Form.Item>
            </Form>
        </>
    )
}
