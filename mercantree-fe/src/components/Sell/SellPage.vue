<template>
  <div>
        <h1 class="text-xl mb-12 font-bold">Lista de Vendas</h1>

        <div class="my-4 flex justify-between">
            <router-link to="/sell/create" class="btn btn-success btn-sm text-base-100">Adicionar</router-link>

            <select v-model="ordering"
            @change="listOrders()"
            class="select select-sm select-bordered ml-auto mr-4">
                <option value="" disabled selected>Ordenar</option>
                <option value="created">Data-ASC</option>
                <option value="-created">Data-DESC</option>
            </select>
        </div>

        <div v-if="orders.count == 0">
            Nenhuma venda encontrado
        </div>

        <mt-table :table="table" v-else >
            <tr v-for="order in orders.results">
                <th></th>
                <th>R${{ order.payment.amount }}</th>
                <th>{{ format_date(order.created ?? '') }}</th>
                <th>{{ order.status }}</th>
                <th>
                    <font-awesome-icon class="text-success" v-if="order.payment.is_paid" icon="check" />
                    <font-awesome-icon class="text-warning" v-else icon="warning" />
                </th>
                <th>{{ order.user }}</th>
                <th>
                    <router-link :to="`/sell/order/${order.id}`" class="btn btn-success text-base-100 btn-sm">View</router-link>
                </th>
            </tr>
        </mt-table>

        <div class="w-full flex justify-center mt-4">
            <div class="btn-group">
                <button class="btn btn-sm"
                v-for="page in pages"
                :class="{'btn-active': page == activePage}"
                @click="activePage = page, listOrders()">{{ page }}</button>
            </div>
        </div>

        <div class="modal modal-open" v-if="creationModal">
            <div class="modal-box max-w-2xl">
                <h3 class="font-bold text-lg">Nova venda</h3>
            </div>
        </div>
    </div>
</template>

<script lang="ts">

import MtTable from '../MtTable.vue'
import { defineComponent, ref, onBeforeMount } from 'vue'
import Order from '../../interfaces/orders/order.interface'
import { APIListResponse } from '../../interfaces/common/response.interface'
import { PAGE_SIZE } from '../../consts'
import { computed } from '@vue/reactivity'
import format_date from '../../utils/format_date'
import OrderService from '../../services/orderService'

export default defineComponent({
    components: {
        MtTable,
    },
    methods: {
        format_date,
    },
    setup() {
        const error = ref()
        const table = {
            name: 'Vendas',
            fields: [
                '',
                'Valor',
                'Data',
                'Status',
                'Pagamento',
                'Cadastrante',
                '',
            ]
        }
        const isLoading = ref(false)
        const creationModal = ref(false)
        const activePage = ref(1)
        const ordering = ref('')
        const orders = ref<APIListResponse<Order>>({count: 0, results: []})
        const pages = computed(() => Math.floor((orders.value.count + PAGE_SIZE - 1) / PAGE_SIZE))

        const listOrders = async () => {
            try {
                isLoading.value = true
                const response = await OrderService().list(activePage.value, '', ordering.value)
                isLoading.value = false

                orders.value = response
            }
            catch(e) {
                error.value = e
            }
        }

        onBeforeMount(listOrders)

        return {
            error,
            isLoading,
            orders,
            ordering,
            listOrders,
            pages,
            activePage,
            table,
            creationModal,
        }
    },
})

</script>

<style>
</style>