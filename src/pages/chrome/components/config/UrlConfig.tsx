import { useMemo, useContext, } from 'react'
import { useBoolean, } from 'ahooks';
import { Button, Input, Form, Switch, Modal } from 'antd'
import { ConfigContext } from '@/rootContext';

//url配置
export default function UrlConfig() {
    const { config, updateConfig, } = useContext(ConfigContext);
    const [open, { toggle }] = useBoolean();
    const [form] = Form.useForm();
    const urlValue = Form.useWatch('url', form)
    const onSubmit = async ({ url, use_url }) => {
        if (url) {
            url = url.split('\n')
            url = url.map((item: string) => item.trim()).filter((item: string) => item)
        } else {
            url = []
        }
        await updateConfig({ ...config, url, use_url })
        toggle()
    }

    const urlLens = useMemo(() => {
        if (Array.isArray(urlValue)) {
            return urlValue.filter(it => it).length
        } else {
            return urlValue?.split('\n').filter((it: any) => it).length || 0
        }
    }, [urlValue])

    return (
        <>
            <Button size='large' onClick={toggle}>启动网址</Button>
            <Modal
                title='启动网址'
                open={open}
                destroyOnHidden
                mask={false}
                onCancel={toggle}
                onOk={form.submit}
            >
                <Form
                    form={form}
                    onFinish={onSubmit}
                    initialValues={{
                        url: config.url.join('\n'),
                        use_url: config.use_url,
                    }}
                >
                    <Form.Item
                        name='url'
                        extra={`当前url数量：${urlLens}`}
                    >
                        <Input.TextArea rows={8} />
                    </Form.Item>
                    <Form.Item
                        label='是否启用'
                        name='use_url'
                    >
                        <Switch checkedChildren='启用' unCheckedChildren='禁用' />
                    </Form.Item>
                </Form>
            </Modal>
        </>
    )
}