============================================================================
多対多の関連を持つオブジェクトをチェックボックスで編集可能なフォーム
============================================================================

課題: 商品登録画面の実装
============================================================================

多対多の関連を持つオブジェクトの編集画面について、
販売管理システムの商品登録画面を例に考えてみます。

商品登録画面では、商品に関する基本情報と商品カテゴリを登録可能です。
画面のイメージは下図の通りです。

.. figure:: images/habtm_checkbox_form.png
  :scale: 80%

  販売管理システム - 商品登録画面

今回のサンプルは、 :ref:`many_to_many_object_registrable_form` の課題と
実現したいことは同じです。
商品カテゴリの選択がプルダウン形式のセレクトボックスからチェックボックスに変わっています。

DB設計は以下の通りです。

.. figure:: images/mtm_db_er.png
  :scale: 80%

  販売管理システムDB設計 - ER図

モデル、システム要件、に関しては
:ref:`many_to_many_object_registrable_form` と全く同じのため省略いたします。


多対多の関連をチェックボックスで登録する方法
============================================================================

今回は以下3つの項目に分けて解説を行います。

- 関連をidsメソッドを利用して更新する方法
- 多対多の関連をチェックボックスで更新するViewの実装方法
- 多対多の関連をids=で更新するControllerの実装方法


関連をidsメソッドを利用して更新する方法
----------------------------------------------------------------------------

モデルのidsメソッドを利用することで、関連オブジェクトのid取得と関連の追加/削除を行うことができます。
Product(商品)とCategory(カテゴリ)は多対多の関係にあります。
商品のカテゴリid一覧は、category_ids で取得が可能です。

.. code-block:: ruby

  # 1商品に紐づくカテゴリを取得
  irb(main):002:0> Product.first.categories
  => #<ActiveRecord::Associations::CollectionProxy
  [#<Category id: 1, name: "機械部品", created_at: "2014-11-03 16:39:35", updated_at: "2014-11-03 16:39:35">,
   #<Category id: 3, name: "素材・材料", created_at: "2014-11-03 16:39:35", updated_at: "2014-11-03 16:39:35">]>

.. code-block:: ruby

  # 商品に紐づくカテゴリのidのみ、idsで取得
  irb(main):003:0> Product.first.category_ids
  => [1, 3]


Productモデルのcategory_idsにカテゴリのid配列を渡すことで、商品に紐づくカテゴリの更新が可能です。
更新するidsは、商品と1対多の関連にある商品カテゴリの product_category_ids ではなく、
多対多の関連にあるカテゴリのcategory_idsであることに注意してください。

.. code-block:: ruby

  # 初期状態では、商品はカテゴリ「機械部品(1)」「素材・材料(3)」のカテゴリを持っている
  irb(main):005:0> Product.first.category_ids
  => [1, 3]

.. code-block:: ruby

  # idsメソッドを利用して、商品に紐づくカテゴリを「電子部品(2)」だけに変更する
  irb(main):006:0> Product.first.category_ids = [2]
   (0.1ms)  BEGIN
  DELETE FROM `product_categories` WHERE `product_categories`.`product_id` = 1 AND `product_categories`.`category_id` IN (1, 3)
  INSERT INTO `product_categories` (`category_id`, `created_at`, `product_id`, `updated_at`) VALUES (2, '2014-11-05 16:42:55', 1, '2014-11-05 16:42:55')
   (0.4ms)  COMMIT
  => [2]

.. code-block:: ruby

  # 再度、商品のカテゴリを参照し、更新されていることを確認する
  irb(main):007:0> Product.first.categories
  => #<ActiveRecord::Associations::CollectionProxy
     [#<Category id: 2, name: "電子部品", created_at: "2014-11-03 16:39:35", updated_at: "2014-11-03 16:39:35">]>



多対多の関連をチェックボックスで更新するViewの実装方法
----------------------------------------------------------------------------

商品のカテゴリを更新する、Viewの実装は以下のようになります。

.. code-block:: ruby

  # app/views/product/new.html.erb (一部重要な部分のみ抜粋)
  # edit.html.erb もpost先以外は同じ

  <%= form_for(@product, url: path, method: method) do |f| %>

    # 省略

    <div class="col-sm-12">
      <% f.object.selectable_categories.each do |category| %>
        <%= f.label :category_ids, value: category.id, class: 'checkbox' do %>
          <%= f.check_box :category_ids, { multiple: true }, category.id, nil %>
          <%= category.name %>
        <% end %>
      <% end %>
    </div>

    <%= f.submit '登録', class: 'btn btn-primary' %>
  <% end %>

:ref:`many_to_many_object_registrable_form` では、fields_for に指定するオブジェクトは、
商品(Product)モデルと1対多の関連にある商品カテゴリ(ProductCategory)モデルでした。

チェックボックス形式で商品のカテゴリを更新する際は、商品(Product)モデルと
多対多の関連にあるカテゴリ(Category)のidsを、check_boxとして指定します。

このようにViewを実装すると、Controller側には以下のようにパラメータが渡されます。

.. code-block:: ruby

  # paramsの例
  "form_product"=>{"code"=>"", "name"=>"", "name_kana"=>"", "price"=>"",
                   "purchase_cost"=>"", "availability"=>"false",
                   "category_ids"=>["2", "3"]},
   "commit"=>"登録",
   "action"=>"create",
   "controller"=>"products"}

多対多の関連をids=で更新するControllerの実装方法
----------------------------------------------------------------------------

商品に紐づくカテゴリをcategory_ids=で更新する方法と、
Viewからcategory_idsを飛ばす方法については検討しました。

controller側で商品カテゴリを更新するコードは、以下のようになります。

.. code-block:: ruby

  # app/controller/products.rb
  def create
    @product = Form::Product.new(product_params)
    if @product.save
      redirect_to products_path, notice: "商品 #{@product.name} を登録しました。"
    else
      render :new
    end
  end

  def update
    @product = Form::Product.find(params[:id])
    if @product.update_attributes(product_params)
      redirect_to products_path, notice: "商品 #{@product.name} を更新しました。"
    else
      render :edit
    end
  end

.. note::

  update関数内で、``@product.attributes = product_params`` を利用してはいけません。
  ids= メソッドを利用している場合、attributesに値を入れた時点で、
  (トランザクションを張っていても) DBへのデータ登録が実施されてしまうためです。

サンプルアプリケーション
============================================================================

今回実装したサンプルアプリケーションは、以下ページにて取得可能です。

- https://github.com/Rails-Application-Build-Guides/rails-application-build-guide-sample/tree/master/form/many_to_many_checkbox_forms
